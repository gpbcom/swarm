from __future__ import annotations

# Standard library imports
from http import HTTPStatus
from logging import Logger, getLogger
from typing import ClassVar, List, Optional
from uuid import UUID

# Third-party imports
from fastapi import APIRouter, Depends

# First-party imports
from swarm_api.dependencies.route_access import RouteAccess
from swarm_models.operators.operator import Operator
from swarm_models.operators.operator_created import OperatorCreated
from swarm_models.operators.operator_directory_entry import OperatorDirectoryEntry
from swarm_models.operators.operator_entry import OperatorEntry
from swarm_models.people.enums import RoleName
from swarm_service.gateway.operators.operator_service import OperatorService


class OperatorRouter(APIRouter):
    """The ``/v1/operators`` routes of the gateway: the directory of Operators and the creation of one.

    Attributes:
        POST (ClassVar[str]): The method of a creation.
        GET (ClassVar[str]): The method of a read.
        COLLECTION_PATH (ClassVar[str]): The path of the directory.
        ITEM_PATH (ClassVar[str]): The path of one Operator.
        ADMINISTRATOR_ROLES (ClassVar[List[RoleName]]): The roles that may list and create Operators.
        OPERATOR_ROLES (ClassVar[List[RoleName]]): The roles that may read their own Operator.
        operators (OperatorService): The service that holds the rules of an Operator.
        logger (Logger): Logger instance.

    Notes:
        - **Each route only delegates**: the rules live in ``OperatorService``.
        - The Operator of a call is checked by ``RouteAccess`` from the ``operator_id`` of the path, so another
          Operator's identifier is answered as not found.
    """

    POST: ClassVar[str] = "POST"
    GET: ClassVar[str] = "GET"
    COLLECTION_PATH: ClassVar[str] = "/operators"
    ITEM_PATH: ClassVar[str] = "/operators/{operator_id}"
    ADMINISTRATOR_ROLES: ClassVar[List[RoleName]] = [RoleName.SWARM_ADMINISTRATOR]
    OPERATOR_ROLES: ClassVar[List[RoleName]] = [role for role in RoleName if role != RoleName.SWARM_ADMINISTRATOR]

    def __init__(self, operators: OperatorService, logger: Optional[Logger] = None) -> None:
        """Initialise the router and declare its routes.

        Args:
            operators (OperatorService): The service that holds the rules of an Operator.
            logger (Optional[Logger]): Logger instance.
        """
        super().__init__()
        self.logger = logger if logger else getLogger(__name__)
        self.operators = operators
        self.add_api_route(
            self.COLLECTION_PATH,
            self.create_operator,
            methods=[self.POST],
            status_code=HTTPStatus.CREATED,
            response_model=OperatorCreated,
            dependencies=[Depends(RouteAccess(self.ADMINISTRATOR_ROLES))],
        )
        self.add_api_route(
            self.COLLECTION_PATH,
            self.list_operators,
            methods=[self.GET],
            response_model=List[OperatorDirectoryEntry],
            dependencies=[Depends(RouteAccess(self.ADMINISTRATOR_ROLES))],
        )
        self.add_api_route(
            self.ITEM_PATH,
            self.read_operator,
            methods=[self.GET],
            response_model=Operator,
            dependencies=[Depends(RouteAccess(self.OPERATOR_ROLES))],
        )
        self.logger.debug("The Operator routes are declared.")

    ############################
    # Publicly Exposed Methods #
    ############################

    async def create_operator(self, entry: OperatorEntry) -> OperatorCreated:
        """Create one Operator.

        Args:
            entry (OperatorEntry): The entry form.

        Returns:
            OperatorCreated: The Operator, its cell assignment and its first Mission planner.
        """
        return await self.operators.create(entry)

    async def list_operators(
        self, after: Optional[UUID] = None, limit: int = OperatorService.PAGE_SIZE_DEFAULT
    ) -> List[OperatorDirectoryEntry]:
        """List the Operators of the directory.

        Args:
            after (Optional[UUID]): The last Operator of the previous page.
            limit (int): The size of the page.

        Returns:
            List[OperatorDirectoryEntry]: One page of the directory.
        """
        return await self.operators.list(after, limit)

    async def read_operator(self, operator_id: UUID) -> Operator:
        """Read one Operator.

        Args:
            operator_id (UUID): The Operator.

        Returns:
            Operator: The Operator.
        """
        return await self.operators.get(operator_id)
