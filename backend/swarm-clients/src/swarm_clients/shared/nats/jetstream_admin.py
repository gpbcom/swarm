from __future__ import annotations

# Standard library imports
from logging import Logger, getLogger
from typing import ClassVar, List, Optional

# Third-party imports
from nats.aio.client import Client
from nats.errors import Error as NatsError
from nats.js.api import ExternalStream, RetentionPolicy, StorageType, StreamConfig
from nats.js.api import StreamSource as NatsStreamSource
from nats.js.errors import Error as JetStreamError
from nats.js.errors import NotFoundError

# First-party imports
from swarm_models.enums import StreamRetention, StreamStorage
from swarm_models.streams.stream_source import StreamSource
from swarm_models.streams.stream_spec import StreamSpec
from swarm_nats.models.bus.exceptions import SENatsStreamError


class JetStreamAdmin:
    """Creates and updates JetStream streams from their specification.

    Attributes:
        EXTERNAL_API_TEMPLATE (ClassVar[str]): The API prefix of the JetStream domain of a source.
        connection (Client): The connected NATS client.
        logger (Logger): Logger instance.

    Notes:
        - A source with a domain is read through the API of that domain, which is how a cell copies the stream of an
          edge across a leaf node.
        - **A stream that exists is updated, never deleted**, so its messages are kept.
    """

    EXTERNAL_API_TEMPLATE: ClassVar[str] = "$JS.{domain}.API"

    def __init__(self, connection: Client, logger: Optional[Logger] = None) -> None:
        """Keep the connection.

        Args:
            connection (Client): The connected NATS client.
            logger (Optional[Logger]): Logger instance.
        """
        self.connection = connection
        self.logger = logger if logger else getLogger(__name__)

    ############################
    # Internal Helpers Methods #
    ############################

    def _storage(self, storage: StreamStorage) -> StorageType:
        """Map a storage to the one of nats-py.

        Args:
            storage (StreamStorage): The storage of the specification.

        Returns:
            StorageType: The storage of nats-py.
        """
        match storage:
            case StreamStorage.FILE:
                self.logger.debug("Mapped the storage to file.")
                return StorageType.FILE
            case StreamStorage.MEMORY:
                self.logger.debug("Mapped the storage to memory.")
                return StorageType.MEMORY

    def _retention(self, retention: StreamRetention) -> RetentionPolicy:
        """Map a retention to the policy of nats-py.

        Args:
            retention (StreamRetention): The retention of the specification.

        Returns:
            RetentionPolicy: The policy of nats-py.
        """
        match retention:
            case StreamRetention.LIMITS:
                self.logger.debug("Mapped the retention to limits.")
                return RetentionPolicy.LIMITS
            case StreamRetention.INTEREST:
                self.logger.debug("Mapped the retention to interest.")
                return RetentionPolicy.INTEREST
            case StreamRetention.WORK_QUEUE:
                self.logger.debug("Mapped the retention to work queue.")
                return RetentionPolicy.WORK_QUEUE

    def _source(self, source: StreamSource) -> NatsStreamSource:
        """Map a source to the one of nats-py.

        Args:
            source (StreamSource): The source of the specification.

        Returns:
            NatsStreamSource: The source of nats-py, with its external API when it has a domain.
        """
        external: Optional[ExternalStream] = None
        if source.domain is not None:
            self.logger.debug("Source %s is read through the domain %s.", source.name, source.domain)
            external = ExternalStream(api=self.EXTERNAL_API_TEMPLATE.format(domain=source.domain))
        else:
            self.logger.debug("Source %s is read from the local domain.", source.name)
        return NatsStreamSource(name=source.name, filter_subject=source.filter_subject, external=external)

    def _config(self, spec: StreamSpec) -> StreamConfig:
        """Map a specification to the configuration of nats-py.

        Args:
            spec (StreamSpec): The specification.

        Returns:
            StreamConfig: The configuration of nats-py.
        """
        sources: Optional[List[NatsStreamSource]] = None
        if spec.sources:
            self.logger.debug("Stream %s has %d sources.", spec.name, len(spec.sources))
            sources = [self._source(source) for source in spec.sources]
        else:
            self.logger.debug("Stream %s has no source.", spec.name)
        return StreamConfig(
            name=spec.name,
            subjects=list(spec.subjects),
            num_replicas=spec.replicas,
            storage=self._storage(spec.storage),
            retention=self._retention(spec.retention),
            duplicate_window=spec.duplicate_window_s,
            sources=sources,
        )

    ############################
    # Publicly Exposed Methods #
    ############################

    async def ensure_stream(self, spec: StreamSpec) -> None:
        """Create a stream, or update it when it exists.

        Args:
            spec (StreamSpec): The specification of the stream.

        Raises:
            SENatsStreamError: When the server refuses to create or to change the stream.
        """
        config = self._config(spec)
        jetstream = self.connection.jetstream()
        try:
            exists = True
            try:
                await jetstream.stream_info(spec.name)
            except NotFoundError:
                self.logger.debug("Stream %s does not exist yet.", spec.name)
                exists = False
            if exists:
                await jetstream.update_stream(config)
                self.logger.info("Updated stream %s.", spec.name)
            else:
                await jetstream.add_stream(config)
                self.logger.info("Created stream %s.", spec.name)
        except (JetStreamError, NatsError) as error:
            self.logger.error("Could not ensure stream %s: %s.", spec.name, type(error).__name__)
            raise SENatsStreamError(
                f"Invalid stream: {spec.name!r}. The server refused it with {type(error).__name__}."
            ) from error
