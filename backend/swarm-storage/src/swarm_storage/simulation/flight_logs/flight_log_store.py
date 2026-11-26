from __future__ import annotations

# Standard library imports
import sqlite3
from logging import Logger, getLogger
from pathlib import Path
from typing import ClassVar, List, Optional
from uuid import UUID

# First-party imports
from swarm_models.simulation.flight_logs.exceptions import (
    SEFlightLogStoreNotSimulatedError,
    SEFlightLogStoreUnwritableError,
)
from swarm_models.simulation.flight_logs.flight_log_entry import FlightLogEntry


class FlightLogStore:
    """The Flight log of simulated flights, written to SQLite at the edge.

    Attributes:
        CREATE_TABLE (str): The statement that creates the table.
        INSERT_ENTRY (str): The statement that stores one entry.
        SELECT_ENTRIES (str): The statement that reads the entries of one Mission.
        path (str): The path of the SQLite file.
        connection (Optional[sqlite3.Connection]): The open connection, or None.
        logger (Logger): Logger instance.

    Notes:
        - **BR-014 requires every entry to be marked as simulated**, so the table refuses any row whose
          ``simulated`` column is not 1, whatever writes to it.
        - Each append is committed at once, so that a crash keeps what was written.
    """

    CREATE_TABLE: ClassVar[str] = (
        "CREATE TABLE IF NOT EXISTS flight_log_entries ("
        "mission_id TEXT NOT NULL, "
        "drone_id TEXT, "
        "t_us INTEGER NOT NULL, "
        "kind TEXT NOT NULL, "
        "seq INTEGER, "
        "detail TEXT, "
        "simulated INTEGER NOT NULL CHECK (simulated = 1))"
    )
    INSERT_ENTRY: ClassVar[str] = (
        "INSERT INTO flight_log_entries (mission_id, drone_id, t_us, kind, seq, detail, simulated) "
        "VALUES (?, ?, ?, ?, ?, ?, 1)"
    )
    SELECT_ENTRIES: ClassVar[str] = (
        "SELECT mission_id, drone_id, t_us, kind, seq, detail FROM flight_log_entries "
        "WHERE mission_id = ? ORDER BY t_us, rowid"
    )

    def __init__(self, path: str, logger: Optional[Logger] = None) -> None:
        """Prepare the store without touching the disk.

        Args:
            path (str): The path of the SQLite file.
            logger (Optional[Logger]): Logger instance.
        """
        self.path = path
        self.connection: Optional[sqlite3.Connection] = None
        self.logger = logger if logger else getLogger(__name__)

    ############################
    # Internal Helpers Methods #
    ############################

    def _require_connection(self) -> sqlite3.Connection:
        """Give the open connection.

        Returns:
            sqlite3.Connection: The open connection.

        Raises:
            SEFlightLogStoreUnwritableError: When the store is not open.
        """
        if self.connection is None:
            self.logger.error("The Flight log store is not open.")
            raise SEFlightLogStoreUnwritableError("The Flight log store is not open.")
        self.logger.debug("The Flight log store is open.")
        return self.connection

    ############################
    # Publicly Exposed Methods #
    ############################

    def open(self) -> None:
        """Create the folder and the table when missing, and open the file.

        Raises:
            SEFlightLogStoreUnwritableError: When the file cannot be opened or the table created.
        """
        try:
            Path(self.path).parent.mkdir(parents=True, exist_ok=True)
            self.connection = sqlite3.connect(self.path)
            self.connection.execute(self.CREATE_TABLE)
            self.connection.commit()
        except (sqlite3.Error, OSError) as error:
            self.logger.error("Cannot open the Flight log store: %s.", type(error).__name__)
            self.close()
            raise SEFlightLogStoreUnwritableError("Cannot open the Flight log store.") from error
        self.logger.info("Opened the Flight log store.")

    def append(self, entry: FlightLogEntry) -> None:
        """Store one entry and commit it.

        Args:
            entry (FlightLogEntry): The entry, which must be simulated.

        Raises:
            SEFlightLogStoreNotSimulatedError: When the entry is not simulated.
            SEFlightLogStoreUnwritableError: When SQLite cannot write it.
        """
        if entry.simulated is not True:
            self.logger.error("Refused a Flight log entry that is not simulated.")
            raise SEFlightLogStoreNotSimulatedError("Refused a Flight log entry that is not simulated.")
        connection = self._require_connection()
        drone_id: Optional[str] = None
        if entry.drone_id is not None:
            drone_id = str(entry.drone_id)
        else:
            self.logger.debug("The entry concerns the whole Squad.")
        try:
            connection.execute(
                self.INSERT_ENTRY,
                (str(entry.mission_id), drone_id, entry.t_us, entry.kind.value, entry.seq, entry.detail),
            )
            connection.commit()
        except sqlite3.Error as error:
            self.logger.error("Cannot write a Flight log entry: %s.", type(error).__name__)
            raise SEFlightLogStoreUnwritableError("Cannot write a Flight log entry.") from error
        self.logger.debug("Appended a Flight log entry.")

    def entries(self, mission_id: UUID) -> List[FlightLogEntry]:
        """Read the entries of one Mission.

        Args:
            mission_id (UUID): The Mission.

        Returns:
            List[FlightLogEntry]: The entries, ordered by moment then insertion.

        Raises:
            SEFlightLogStoreUnwritableError: When SQLite cannot read them.
        """
        connection = self._require_connection()
        try:
            rows = connection.execute(self.SELECT_ENTRIES, (str(mission_id),)).fetchall()
        except sqlite3.Error as error:
            self.logger.error("Cannot read the Flight log entries: %s.", type(error).__name__)
            raise SEFlightLogStoreUnwritableError("Cannot read the Flight log entries.") from error
        self.logger.debug("Read %d Flight log entries.", len(rows))
        return [
            FlightLogEntry(mission_id=row[0], drone_id=row[1], t_us=row[2], kind=row[3], seq=row[4], detail=row[5])
            for row in rows
        ]

    def close(self) -> None:
        """Close the connection, and do nothing when there is none."""
        if self.connection is None:
            self.logger.debug("Nothing to close in the Flight log store.")
            return
        try:
            self.connection.close()
        except sqlite3.Error as error:
            self.logger.error("Cannot close the Flight log store: %s.", type(error).__name__)
            raise
        finally:
            self.connection = None
        self.logger.info("Closed the Flight log store.")
