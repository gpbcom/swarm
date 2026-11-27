from __future__ import annotations

# Standard library imports
from datetime import datetime
from typing import ClassVar, Dict, List, Union
from uuid import UUID

# Third-party imports
import asyncpg

# First-party imports
from swarm_models.enums import Language
from swarm_models.people.person import Person
from swarm_storage.gateway.ddl.operator_directory_tables import OperatorDirectoryTables
from swarm_storage.shared.postgres.repositories.postgres_repository import PostgresRepository


class PersonRepository(PostgresRepository[Person]):
    """The people of the Operators, isolated by row-level security.

    Attributes:
        TABLE (str): The people table.
        OPERATOR_COLUMN (str): The column of the owning Operator.
        NAME_COLUMN (str): The column of the name.
        EMAIL_COLUMN (str): The column of the email address.
        LANGUAGE_COLUMN (str): The column of the language.

    Notes:
        - **Nothing here filters by Operator**: row-level security does, so a query without an Operator finds no person.
        - A person without an Operator is written with a null Operator, which the policy refuses.
    """

    TABLE: ClassVar[str] = OperatorDirectoryTables.PEOPLE_TABLE
    OPERATOR_COLUMN: ClassVar[str] = "operator_id"
    NAME_COLUMN: ClassVar[str] = "name"
    EMAIL_COLUMN: ClassVar[str] = "email"
    LANGUAGE_COLUMN: ClassVar[str] = "language"

    ############################
    # Internal Helpers Methods #
    ############################

    def to_values(self, model: Person) -> Dict[str, Union[str, int, UUID, datetime, List[str]]]:
        """Map a person to the columns it writes.

        Args:
            model (Person): The person.

        Returns:
            Dict[str, Union[str, int, UUID, datetime, List[str]]]: The identifier, the Operator, the name, the email
                address and the language.
        """
        values: Dict[str, Union[str, int, UUID, datetime, List[str]]] = {self.ID_COLUMN: model.id}
        if model.operator_id is not None:
            values[self.OPERATOR_COLUMN] = model.operator_id
        else:
            self.logger.debug("Person %s has no Operator, so the column stays null.", model.id)
        values[self.NAME_COLUMN] = model.name
        values[self.EMAIL_COLUMN] = model.email
        values[self.LANGUAGE_COLUMN] = str(model.language)
        return values

    def to_model(self, record: asyncpg.Record) -> Person:
        """Map a row to its person.

        Args:
            record (asyncpg.Record): The row.

        Returns:
            Person: The person.
        """
        return Person(
            id=record[self.ID_COLUMN],
            operator_id=record[self.OPERATOR_COLUMN],
            name=record[self.NAME_COLUMN],
            email=record[self.EMAIL_COLUMN],
            language=Language(record[self.LANGUAGE_COLUMN]),
        )
