from __future__ import annotations

# Standard library imports
from datetime import datetime
from typing import ClassVar, Dict, List, Optional, Union
from uuid import UUID

# Third-party imports
import asyncpg

# First-party imports
from swarm_models.enums import Anchoring, Deployment, Jurisdiction, LlmProvider
from swarm_models.operators.operator import Operator
from swarm_models.storage.exceptions import SEStorageDuplicateError
from swarm_storage.gateway.ddl.operator_directory_tables import OperatorDirectoryTables
from swarm_storage.shared.postgres.repositories.postgres_repository import PostgresRepository


class OperatorRepository(PostgresRepository[Operator]):
    """The Operators, global to every cell.

    Attributes:
        TABLE (str): The Operators table.
        NAME_COLUMN (str): The column of the name.
        DEPLOYMENT_COLUMN (str): The column of the deployment.
        JURISDICTIONS_COLUMN (str): The column of the jurisdictions, a text array.
        LLM_PROVIDER_COLUMN (str): The column of the language model provider.
        ANCHORING_COLUMN (str): The column of the anchoring.
        NAME_QUERY (str): The query that finds an Operator by its trimmed, case-insensitive name.

    Notes:
        - A second Operator whose name matches an existing one, ignoring case and surrounding spaces, raises
          ``SEStorageDuplicateError``: the unique index of the table decides, so two requests cannot both win.
    """

    TABLE: ClassVar[str] = OperatorDirectoryTables.OPERATORS_TABLE
    NAME_COLUMN: ClassVar[str] = "name"
    DEPLOYMENT_COLUMN: ClassVar[str] = "deployment"
    JURISDICTIONS_COLUMN: ClassVar[str] = "jurisdictions"
    LLM_PROVIDER_COLUMN: ClassVar[str] = "llm_provider"
    ANCHORING_COLUMN: ClassVar[str] = "anchoring"
    NAME_QUERY: ClassVar[str] = "SELECT * FROM {schema}.{table} WHERE lower(btrim(name)) = lower(btrim($1))"

    ############################
    # Internal Helpers Methods #
    ############################

    def to_values(self, model: Operator) -> Dict[str, Union[str, int, UUID, datetime, List[str]]]:
        """Map an Operator to the columns it writes.

        Args:
            model (Operator): The Operator.

        Returns:
            Dict[str, Union[str, int, UUID, datetime, List[str]]]: The identifier, the name, the choices and the
                jurisdictions as a list of text.
        """
        return {
            self.ID_COLUMN: model.id,
            self.NAME_COLUMN: model.name,
            self.DEPLOYMENT_COLUMN: str(model.deployment),
            self.JURISDICTIONS_COLUMN: [str(jurisdiction) for jurisdiction in model.jurisdictions],
            self.LLM_PROVIDER_COLUMN: str(model.llm_provider),
            self.ANCHORING_COLUMN: str(model.anchoring),
        }

    def to_model(self, record: asyncpg.Record) -> Operator:
        """Map a row to its Operator.

        Args:
            record (asyncpg.Record): The row.

        Returns:
            Operator: The Operator.
        """
        return Operator(
            id=record[self.ID_COLUMN],
            name=record[self.NAME_COLUMN],
            deployment=Deployment(record[self.DEPLOYMENT_COLUMN]),
            jurisdictions=[Jurisdiction(value) for value in record[self.JURISDICTIONS_COLUMN]],
            llm_provider=LlmProvider(record[self.LLM_PROVIDER_COLUMN]),
            anchoring=Anchoring(record[self.ANCHORING_COLUMN]),
        )

    ############################
    # Publicly Exposed Methods #
    ############################

    async def add(self, model: Operator) -> Operator:
        """Insert an Operator.

        Args:
            model (Operator): The Operator to store.

        Returns:
            Operator: The same Operator.

        Raises:
            SEStorageDuplicateError: If another Operator has the same name, ignoring case and surrounding spaces.
        """
        try:
            return await super().add(model)
        except asyncpg.exceptions.UniqueViolationError as error:
            self.logger.error("The Operator %s was refused: its name is already taken.", model.id)
            raise SEStorageDuplicateError("The Operator is refused: its name is already taken.") from error

    async def find_by_name(self, name: str) -> Optional[Operator]:
        """Find an Operator by its name, ignoring case and surrounding spaces.

        Args:
            name (str): The name to look for.

        Returns:
            Optional[Operator]: The Operator, or none if no name matches.
        """
        record = await self.unit_of_work.connection.fetchrow(self.NAME_QUERY.format(**self.names()), name)
        if record is None:
            self.logger.debug("No Operator has the requested name.")
            return None
        return self.to_model(record)
