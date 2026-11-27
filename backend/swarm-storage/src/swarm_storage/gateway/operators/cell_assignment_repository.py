from __future__ import annotations

# Standard library imports
from datetime import datetime
from typing import ClassVar, Dict, List, Union
from uuid import UUID

# Third-party imports
import asyncpg

# First-party imports
from swarm_models.operators.cell_assignment import CellAssignment
from swarm_storage.gateway.ddl.operator_directory_tables import OperatorDirectoryTables
from swarm_storage.shared.postgres.repositories.postgres_repository import PostgresRepository


class CellAssignmentRepository(PostgresRepository[CellAssignment]):
    """The cell each Operator is assigned to, global to every Operator.

    Attributes:
        TABLE (str): The cell assignments table.
        ID_COLUMN (str): The primary key, which is the Operator.
        CELL_COLUMN (str): The column of the cell name.
        ASSIGNED_AT_COLUMN (str): The column of the moment of the assignment.

    Notes:
        - The assignment is keyed by its Operator: ``get`` takes the identifier of the Operator.
    """

    TABLE: ClassVar[str] = OperatorDirectoryTables.CELL_ASSIGNMENTS_TABLE
    ID_COLUMN: ClassVar[str] = "operator_id"
    CELL_COLUMN: ClassVar[str] = "cell"
    ASSIGNED_AT_COLUMN: ClassVar[str] = "assigned_at"

    ############################
    # Internal Helpers Methods #
    ############################

    def to_values(self, model: CellAssignment) -> Dict[str, Union[str, int, UUID, datetime, List[str]]]:
        """Map an assignment to the columns it writes.

        Args:
            model (CellAssignment): The assignment.

        Returns:
            Dict[str, Union[str, int, UUID, datetime, List[str]]]: The Operator, the cell and the moment.
        """
        return {
            self.ID_COLUMN: model.operator_id,
            self.CELL_COLUMN: model.cell,
            self.ASSIGNED_AT_COLUMN: model.assigned_at,
        }

    def to_model(self, record: asyncpg.Record) -> CellAssignment:
        """Map a row to its assignment.

        Args:
            record (asyncpg.Record): The row.

        Returns:
            CellAssignment: The assignment.
        """
        return CellAssignment(
            operator_id=record[self.ID_COLUMN],
            cell=record[self.CELL_COLUMN],
            assigned_at=record[self.ASSIGNED_AT_COLUMN],
        )
