from __future__ import annotations

# Standard library imports
from logging import Logger, getLogger
from typing import Optional, Type

# Third-party imports
import ormsgpack
from pydantic import BaseModel

# First-party imports
from swarm_models.live.exceptions import SELiveMessageUnreadable
from swarm_models.live.live_subscription import LiveSubscription
from swarm_models.telemetry.squad_frame import SquadFrame


class LiveCodec:
    """Encode and decode the messages of the live socket as MessagePack.

    Attributes:
        logger (Logger): Logger instance.

    Notes:
        - ``ormsgpack`` serialises the Pydantic models directly.
        - **Decoding validates the model**, so a message of another shape is refused.
        - The broad ``except`` of ``_decode`` turns any failure of the bytes or of a model validator into
          ``SELiveMessageUnreadable``, because the models raise their own exception types.
    """

    def __init__(self, logger: Optional[Logger] = None) -> None:
        """Initialise the codec.

        Args:
            logger (Optional[Logger]): Logger to use. A logger named after the module is used when it is ``None``.
        """
        self.logger = logger if logger else getLogger(__name__)

    ############################
    # Internal Helpers Methods #
    ############################

    def _encode(self, model: BaseModel) -> bytes:
        """Encode a model.

        Args:
            model (BaseModel): The model.

        Returns:
            bytes: The MessagePack bytes.
        """
        data = ormsgpack.packb(model, option=ormsgpack.OPT_SERIALIZE_PYDANTIC)
        self.logger.debug("Encoded %s in %d bytes.", type(model).__name__, len(data))
        return data

    def _decode[M: BaseModel](self, data: bytes, model_type: Type[M]) -> M:
        """Decode and validate a model.

        Args:
            data (bytes): The MessagePack bytes.
            model_type (Type[M]): The expected model.

        Returns:
            M: The model.

        Raises:
            SELiveMessageUnreadable: If the bytes are not MessagePack or not the model.
        """
        try:
            model = model_type.model_validate(ormsgpack.unpackb(data))
        except Exception as error:
            self.logger.error("Refused %d bytes as %s: %s.", len(data), model_type.__name__, type(error).__name__)
            raise SELiveMessageUnreadable(
                f"Unreadable {model_type.__name__}: {type(error).__name__}. Must be valid MessagePack of that model."
            ) from error
        self.logger.debug("Decoded %s from %d bytes.", model_type.__name__, len(data))
        return model

    ############################
    # Publicly Exposed Methods #
    ############################

    def encode_squad_frame(self, squad_frame: SquadFrame) -> bytes:
        """Encode a squad frame.

        Args:
            squad_frame (SquadFrame): The frame.

        Returns:
            bytes: The MessagePack bytes.
        """
        return self._encode(squad_frame)

    def decode_squad_frame(self, data: bytes) -> SquadFrame:
        """Decode a squad frame.

        Args:
            data (bytes): The MessagePack bytes.

        Returns:
            SquadFrame: The frame.

        Raises:
            SELiveMessageUnreadable: If the bytes are not a squad frame.
        """
        return self._decode(data, SquadFrame)

    def encode_subscription(self, subscription: LiveSubscription) -> bytes:
        """Encode a subscription.

        Args:
            subscription (LiveSubscription): The subscription.

        Returns:
            bytes: The MessagePack bytes.
        """
        return self._encode(subscription)

    def decode_subscription(self, data: bytes) -> LiveSubscription:
        """Decode a subscription.

        Args:
            data (bytes): The MessagePack bytes.

        Returns:
            LiveSubscription: The subscription.

        Raises:
            SELiveMessageUnreadable: If the bytes are not a subscription.
        """
        return self._decode(data, LiveSubscription)
