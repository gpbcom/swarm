from __future__ import annotations

# Standard library imports
import asyncio
from datetime import UTC, datetime
from logging import Logger, getLogger
from os import urandom
from time import time_ns
from typing import ClassVar, List, Literal, Optional, Tuple
from uuid import UUID

# First-party imports
from swarm_clients.gateway.keycloak.keycloak_admin_client import KeycloakAdminClient
from swarm_models.enums import Deployment, LlmProvider, OperatorField
from swarm_models.keycloak.exceptions import SEKeycloakConflictError, SEKeycloakUnreachableError
from swarm_models.operators.cell_assignment import CellAssignment
from swarm_models.operators.exceptions import (
    SEOperatorFieldMissingError,
    SEOperatorNameTakenError,
    SEOperatorNotFoundError,
    SEOperatorPlannerEmailTakenError,
)
from swarm_models.operators.operator import Operator
from swarm_models.operators.operator_created import OperatorCreated
from swarm_models.operators.operator_directory_entry import OperatorDirectoryEntry
from swarm_models.operators.operator_entry import OperatorEntry
from swarm_models.people.person import Person
from swarm_models.storage.exceptions import SEStorageDuplicateError
from swarm_storage.gateway.operators.cell_assignment_repository import CellAssignmentRepository
from swarm_storage.gateway.operators.operator_repository import OperatorRepository
from swarm_storage.gateway.people.person_repository import PersonRepository
from swarm_storage.shared.postgres.postgres_pool import PostgresPool


class OperatorService:
    """Everything the gateway does with the Operators: create one, list them and read one.

    Attributes:
        pool (PostgresPool): The pool of the gateway's schema, opened on the first call.
        schema_name (str): The schema of the gateway.
        cell (str): The cell a new Operator is placed in.
        keycloak (KeycloakAdminClient): The client of the Keycloak admin API.
        lock (asyncio.Lock): Serialises the opening of the pool.
        logger (Logger): Logger instance.
        PAGE_SIZE_DEFAULT (int): The page size of ``list`` when none is given.
        FIELD_SEPARATOR (str): What joins the names of the missing fields in a message.
        BYTE_ORDER (Literal["big"]): The byte order of the random bytes of an identifier.
        TIMESTAMP_SHIFT (int): The position of the millisecond timestamp in a version 7 UUID.
        VERSION_7_BITS (int): The version bits of a version 7 UUID.
        VARIANT_BITS (int): The variant bits of a UUID.
        RANDOM_BYTES (int): The number of random bytes behind the timestamp.
        RANDOM_A_BITS (int): The size of the first random part, below the version.
        RANDOM_A_SHIFT (int): The position of the first random part.
        RANDOM_B_BITS (int): The size of the second random part, below the variant.
        NS_PER_MS (int): The nanoseconds in a millisecond.

    Notes:
        - **This class is the one place for the rules of an Operator**: the required fields, the name and the
          defaults.
        - ``create`` works in one unit of work opened for the new Operator, so that row-level security accepts its
          person, and a Keycloak failure rolls the rows back and removes what was made in Keycloak.
        - ``list`` and ``get`` open a unit of work without an Operator, which reads only the global directory tables.
        - The pool opens on the first call, so that building the application needs no database.
    """

    PAGE_SIZE_DEFAULT: ClassVar[int] = 100
    FIELD_SEPARATOR: ClassVar[str] = ", "
    BYTE_ORDER: ClassVar[Literal["big"]] = "big"
    TIMESTAMP_SHIFT: ClassVar[int] = 80
    VERSION_7_BITS: ClassVar[int] = 7 << 76
    VARIANT_BITS: ClassVar[int] = 0b10 << 62
    RANDOM_BYTES: ClassVar[int] = 10
    RANDOM_A_BITS: ClassVar[int] = 12
    RANDOM_A_SHIFT: ClassVar[int] = 64
    RANDOM_B_BITS: ClassVar[int] = 62
    NS_PER_MS: ClassVar[int] = 1_000_000

    def __init__(
        self,
        pool: PostgresPool,
        schema_name: str,
        cell: str,
        keycloak: KeycloakAdminClient,
        logger: Optional[Logger] = None,
    ) -> None:
        """Prepare the service, with nothing opened.

        Args:
            pool (PostgresPool): The pool of the gateway's schema.
            schema_name (str): The schema of the gateway.
            cell (str): The cell a new Operator is placed in.
            keycloak (KeycloakAdminClient): The client of the Keycloak admin API.
            logger (Optional[Logger]): Logger instance.
        """
        self.logger = logger if logger else getLogger(__name__)
        self.pool = pool
        self.schema_name = schema_name
        self.cell = cell
        self.keycloak = keycloak
        self.lock = asyncio.Lock()

    ############################
    # Internal Helpers Methods #
    ############################

    def _new_id(self) -> UUID:
        """Make a version 7 UUID, from the clock and random bytes.

        Returns:
            UUID: A new identifier.
        """
        milliseconds = time_ns() // self.NS_PER_MS
        random = int.from_bytes(urandom(self.RANDOM_BYTES), self.BYTE_ORDER)
        random_b = random & ((1 << self.RANDOM_B_BITS) - 1)
        random_a = (random >> self.RANDOM_B_BITS) & ((1 << self.RANDOM_A_BITS) - 1)
        value = (
            (milliseconds << self.TIMESTAMP_SHIFT)
            | self.VERSION_7_BITS
            | (random_a << self.RANDOM_A_SHIFT)
            | self.VARIANT_BITS
            | random_b
        )
        return UUID(int=value)

    def _check_entry(self, entry: OperatorEntry) -> Tuple[str, Deployment, str]:
        """Check that every required field is given.

        Args:
            entry (OperatorEntry): The request.

        Returns:
            Tuple[str, Deployment, str]: The name, the deployment and the e-mail address of the first Mission planner.

        Raises:
            SEOperatorFieldMissingError: Naming every missing field.
        """
        missing: List[OperatorField] = []
        if entry.name is None:
            missing.append(OperatorField.NAME)
        if entry.deployment is None:
            missing.append(OperatorField.DEPLOYMENT)
        if not entry.jurisdictions:
            missing.append(OperatorField.JURISDICTIONS)
        if entry.first_mission_planner_email is None:
            missing.append(OperatorField.FIRST_MISSION_PLANNER_EMAIL)
        if missing or entry.name is None or entry.deployment is None or entry.first_mission_planner_email is None:
            names = self.FIELD_SEPARATOR.join(field.value for field in missing)
            self.logger.error("The Operator request lacks: %s.", names)
            raise SEOperatorFieldMissingError(f"Missing fields: {names}. Each is required.")
        self.logger.debug("Every required field is given.")
        return entry.name, entry.deployment, entry.first_mission_planner_email

    def _build_operator(self, entry: OperatorEntry, name: str, deployment: Deployment) -> Operator:
        """Build the Operator of a checked request, with its defaults.

        Args:
            entry (OperatorEntry): The request.
            name (str): Its name.
            deployment (Deployment): Where its Swarm runs.

        Returns:
            Operator: The new Operator.
        """
        provider = entry.llm_provider
        if provider is None:
            if deployment == Deployment.ON_PREMISES:
                provider = LlmProvider.OPEN_WEIGHT
            else:
                provider = LlmProvider.CLAUDE
            self.logger.debug("The language model provider defaults to %s.", provider)
        else:
            self.logger.debug("The language model provider is %s, as given.", provider)
        return Operator(
            id=self._new_id(),
            name=name,
            deployment=deployment,
            jurisdictions=entry.jurisdictions,
            llm_provider=provider,
            anchoring=entry.anchoring,
        )

    async def _ensure_open(self) -> None:
        """Open the pool on the first call, once even for concurrent calls."""
        async with self.lock:
            if self.pool.is_open:
                self.logger.debug("The pool is open already.")
                return
            await self.pool.open()

    async def _remove_from_keycloak(self, organisation_id: Optional[str], user_id: Optional[str]) -> None:
        """Remove what was created in Keycloak, and only warn when a removal fails.

        Args:
            organisation_id (Optional[str]): The organisation created, if any.
            user_id (Optional[str]): The user created, if any.
        """
        if user_id is not None:
            try:
                await self.keycloak.delete_user(user_id)
            except SEKeycloakUnreachableError as error:
                self.logger.warning("The Keycloak user %s could not be removed: %s.", user_id, type(error).__name__)
        else:
            self.logger.debug("No Keycloak user to remove.")
        if organisation_id is not None:
            try:
                await self.keycloak.delete_organisation(organisation_id)
            except SEKeycloakUnreachableError as error:
                self.logger.warning(
                    "The Keycloak organisation %s could not be removed: %s.", organisation_id, type(error).__name__
                )
        else:
            self.logger.debug("No Keycloak organisation to remove.")

    async def _invite(self, operator: Operator, person: Person) -> Tuple[str, str]:
        """Create the organisation, then invite the person, and undo it when that fails.

        Args:
            operator (Operator): The new Operator.
            person (Person): Its first Mission planner.

        Returns:
            Tuple[str, str]: The identifiers created in Keycloak, the organisation then the user.

        Raises:
            SEOperatorPlannerEmailTakenError: If Keycloak knows the e-mail address already.
            SEKeycloakUnreachableError: If Keycloak cannot be reached or refuses.
        """
        organisation_id: Optional[str] = None
        try:
            organisation_id = await self.keycloak.create_organisation(operator)
            user_id = await self.keycloak.invite_mission_planner(organisation_id, person)
        except SEKeycloakConflictError as error:
            self.logger.error("The e-mail address of the first Mission planner is known to Keycloak.")
            await self._remove_from_keycloak(organisation_id, None)
            raise SEOperatorPlannerEmailTakenError(
                "The e-mail address of the first Mission planner is already used."
            ) from error
        except SEKeycloakUnreachableError:
            self.logger.error("Keycloak failed while creating the Operator %s.", operator.id)
            await self._remove_from_keycloak(organisation_id, None)
            raise
        return organisation_id, user_id

    ############################
    # Publicly Exposed Methods #
    ############################

    async def create(self, entry: OperatorEntry) -> OperatorCreated:
        """Create an Operator, its cell assignment and its first Mission planner, and invite her.

        Args:
            entry (OperatorEntry): The request.

        Returns:
            OperatorCreated: The Operator, its cell and its first Mission planner.

        Raises:
            SEOperatorFieldMissingError: If a required field is missing.
            SEOperatorNameTakenError: If an Operator has this name already.
            SEOperatorPlannerEmailTakenError: If Keycloak knows the e-mail address of the planner already.
            SEKeycloakUnreachableError: If Keycloak cannot be reached or refuses.
        """
        name, deployment, email = self._check_entry(entry)
        await self._ensure_open()
        operator = self._build_operator(entry, name, deployment)
        person = Person(
            id=self._new_id(),
            operator_id=operator.id,
            name=entry.first_mission_planner_name or email,
            email=email,
        )
        assignment = CellAssignment(operator_id=operator.id, cell=self.cell, assigned_at=datetime.now(UTC))
        created: Optional[Tuple[str, str]] = None
        try:
            async with self.pool.unit_of_work(operator.id) as unit:
                operators = OperatorRepository(unit, self.schema_name)
                if await operators.find_by_name(name) is not None:
                    self.logger.error("The name of the Operator %s is taken.", operator.id)
                    raise SEOperatorNameTakenError("The name of the Operator is already taken.")
                try:
                    await operators.add(operator)
                except SEStorageDuplicateError as error:
                    self.logger.error("The name of the Operator %s was taken in the meantime.", operator.id)
                    raise SEOperatorNameTakenError("The name of the Operator is already taken.") from error
                await CellAssignmentRepository(unit, self.schema_name).add(assignment)
                await PersonRepository(unit, self.schema_name).add(person)
                created = await self._invite(operator, person)
        except Exception as error:
            self.logger.error("The Operator %s was not created: %s.", operator.id, type(error).__name__)
            if created is not None:
                self.logger.debug("The transaction failed after Keycloak, so Keycloak is cleaned.")
                await self._remove_from_keycloak(created[0], created[1])
            else:
                self.logger.debug("Nothing was created in Keycloak that is still there.")
            raise
        self.logger.info("Created the Operator %s in the cell %s.", operator.id, self.cell)
        return OperatorCreated(operator=operator, cell_assignment=assignment, first_mission_planner=person)

    async def list(self, after: Optional[UUID] = None, limit: int = PAGE_SIZE_DEFAULT) -> List[OperatorDirectoryEntry]:
        """List a page of the Operators with their cells, in identifier order.

        Args:
            after (Optional[UUID]): The cursor: only identifiers greater than this one.
            limit (int): The page size.

        Returns:
            List[OperatorDirectoryEntry]: The directory entries of the page.
        """
        await self._ensure_open()
        entries: List[OperatorDirectoryEntry] = []
        async with self.pool.unit_of_work(None) as unit:
            assignments = CellAssignmentRepository(unit, self.schema_name)
            for operator in await OperatorRepository(unit, self.schema_name).list(after, limit):
                assignment = await assignments.get(operator.id)
                if assignment is None:
                    self.logger.warning("The Operator %s has no cell assignment, so it is left out.", operator.id)
                    continue
                entries.append(OperatorDirectoryEntry(operator=operator, cell_assignment=assignment))
        self.logger.debug("Listed %d Operators.", len(entries))
        return entries

    async def get(self, operator_id: UUID) -> Operator:
        """Read one Operator.

        Args:
            operator_id (UUID): Its identifier.

        Returns:
            Operator: The Operator.

        Raises:
            SEOperatorNotFoundError: If no Operator has this identifier.
        """
        await self._ensure_open()
        async with self.pool.unit_of_work(None) as unit:
            operator = await OperatorRepository(unit, self.schema_name).get(operator_id)
        if operator is None:
            self.logger.error("The Operator %s was not found.", operator_id)
            raise SEOperatorNotFoundError(f"Operator not found: {operator_id}.")
        return operator

    async def close(self) -> None:
        """Close the pool, safely before any call and when called twice."""
        await self.pool.close()
        self.logger.debug("The Operator service is closed.")
