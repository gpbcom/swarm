from __future__ import annotations

# Standard library imports
from logging import Logger, getLogger
from os import environ
from typing import ClassVar, Dict, List, Optional

# Third-party imports
import httpx
from pydantic import JsonValue

# First-party imports
from swarm_models.keycloak.exceptions import SEKeycloakConflictError, SEKeycloakUnreachableError
from swarm_models.keycloak.keycloak_admin_config import KeycloakAdminConfig
from swarm_models.operators.operator import Operator
from swarm_models.people.enums import RoleName
from swarm_models.people.person import Person


class KeycloakAdminClient:
    """Creates an Operator's organisation and invites its first Mission planner through the Keycloak admin API.

    Attributes:
        config (KeycloakAdminConfig): The configuration of the connection to Keycloak.
        logger (Logger): Logger instance.
        TOKEN_PATH (str): The path of the token endpoint, below the server URL.
        ADMIN_PATH (str): The path of the admin API, below the server URL.
        ORGANISATIONS_PATH (str): The path of the organisations, below the admin API.
        USERS_PATH (str): The path of the users, below the admin API.
        ROLES_PATH (str): The path of the realm roles, below the admin API.
        MEMBERS_SUFFIX (str): The suffix of the members of an organisation.
        ROLE_MAPPINGS_SUFFIX (str): The suffix of the realm roles of a user.
        ACTIONS_EMAIL_SUFFIX (str): The suffix of the actions e-mail of a user.
        UPDATE_PASSWORD (str): The required action that asks for a new password.
        CONFIGURE_TOTP (str): The required action that sets up multi-factor authentication.
        REQUIRED_ACTIONS (List[str]): The actions the invited person must do at the first sign-in.
        POST (str): The HTTP method that creates.
        GET (str): The HTTP method that reads.
        PUT (str): The HTTP method that replaces or triggers.
        DELETE (str): The HTTP method that deletes.
        AUTHORIZATION_HEADER (str): The name of the header that carries the token.
        BEARER_PREFIX (str): The prefix of the value of the authorization header.
        LOCATION_HEADER (str): The name of the header that carries the address of a new resource.
        PATH_SEPARATOR (str): The separator of the segments of a path.
        ACCESS_TOKEN_KEY (str): The name of the token in the token answer.
        GRANT_TYPE_KEY (str): The form field of the grant type.
        CLIENT_ID_KEY (str): The form field and query parameter of the client identifier.
        CLIENT_SECRET_KEY (str): The form field of the client secret.
        CLIENT_CREDENTIALS (str): The grant type of a service account.
        NAME_KEY (str): The name of the name field of an organisation.
        ALIAS_KEY (str): The name of the alias field of an organisation.
        ATTRIBUTES_KEY (str): The name of the attributes field.
        OPERATOR_ID_ATTRIBUTE (str): The attribute that holds the identifier of the Operator.
        EMAIL_KEY (str): The name of the e-mail field of a user.
        USERNAME_KEY (str): The name of the username field of a user.
        FIRST_NAME_KEY (str): The name of the first name field of a user.
        ENABLED_KEY (str): The name of the enabled field of a user.
        REQUIRED_ACTIONS_KEY (str): The name of the required actions field of a user.

    Notes:
        - A short-lived HTTP client is made for each request, so that nothing stays open.
        - **The secret is read from the environment when a call is made, and neither it nor a token is ever logged.**
        - This is a short request, so it is not an ``AsyncRunnable``.
    """

    TOKEN_PATH: ClassVar[str] = "/realms/{realm}/protocol/openid-connect/token"
    ADMIN_PATH: ClassVar[str] = "/admin/realms/{realm}"
    ORGANISATIONS_PATH: ClassVar[str] = "/organizations"
    USERS_PATH: ClassVar[str] = "/users"
    ROLES_PATH: ClassVar[str] = "/roles"
    MEMBERS_SUFFIX: ClassVar[str] = "/members"
    ROLE_MAPPINGS_SUFFIX: ClassVar[str] = "/role-mappings/realm"
    ACTIONS_EMAIL_SUFFIX: ClassVar[str] = "/execute-actions-email"
    UPDATE_PASSWORD: ClassVar[str] = "UPDATE_PASSWORD"
    CONFIGURE_TOTP: ClassVar[str] = "CONFIGURE_TOTP"
    REQUIRED_ACTIONS: ClassVar[List[str]] = [UPDATE_PASSWORD, CONFIGURE_TOTP]
    POST: ClassVar[str] = "POST"
    GET: ClassVar[str] = "GET"
    PUT: ClassVar[str] = "PUT"
    DELETE: ClassVar[str] = "DELETE"
    AUTHORIZATION_HEADER: ClassVar[str] = "Authorization"
    BEARER_PREFIX: ClassVar[str] = "Bearer "
    LOCATION_HEADER: ClassVar[str] = "Location"
    PATH_SEPARATOR: ClassVar[str] = "/"
    ACCESS_TOKEN_KEY: ClassVar[str] = "access_token"
    GRANT_TYPE_KEY: ClassVar[str] = "grant_type"
    CLIENT_ID_KEY: ClassVar[str] = "client_id"
    CLIENT_SECRET_KEY: ClassVar[str] = "client_secret"
    CLIENT_CREDENTIALS: ClassVar[str] = "client_credentials"
    NAME_KEY: ClassVar[str] = "name"
    ALIAS_KEY: ClassVar[str] = "alias"
    ATTRIBUTES_KEY: ClassVar[str] = "attributes"
    OPERATOR_ID_ATTRIBUTE: ClassVar[str] = "operator_id"
    EMAIL_KEY: ClassVar[str] = "email"
    USERNAME_KEY: ClassVar[str] = "username"
    FIRST_NAME_KEY: ClassVar[str] = "firstName"
    ENABLED_KEY: ClassVar[str] = "enabled"
    REQUIRED_ACTIONS_KEY: ClassVar[str] = "requiredActions"

    def __init__(self, config: KeycloakAdminConfig, logger: Optional[Logger] = None) -> None:
        """Constructur for the KeycloakAdmin class.

        Args:
            config (KeycloakAdminConfig): The Keycloak config loaded from YAML file.
            logger (Optional[Logger]): Optional class logger. Default to None.
        """
        self.config = config
        self.logger = logger if logger else getLogger(__name__)

    ############################
    # Internal Helpers Methods #
    ############################

    def _admin_url(self, path: str) -> str:
        """Build the address of an admin API path.

        Args:
            path (str): The path below the admin API of the realm.

        Returns:
            str: The full address.
        """
        admin_path = self.ADMIN_PATH.format(realm=self.config.realm)
        return f"{self.config.server_url}{admin_path}{path}"

    def _fail(self, message: str, error: Optional[BaseException] = None) -> SEKeycloakUnreachableError:
        """Log a failure at ``ERROR`` and build the error to raise.

        Args:
            message (str): The message of the error.
            error (Optional[BaseException]): The error that caused it, when there is one.

        Returns:
            SEKeycloakUnreachableError: The error to raise.
        """
        if error is not None:
            self.logger.error("%s Cause: %s.", message, type(error).__name__)
        else:
            self.logger.error("%s", message)
        return SEKeycloakUnreachableError(message)

    def _created_id(self, response: httpx.Response) -> str:
        """Read the identifier of a new resource from the ``Location`` header.

        Args:
            response (httpx.Response): The answer to a creation.

        Returns:
            str: The identifier.

        Raises:
            SEKeycloakUnreachableError: When the answer has no ``Location`` header.
        """
        location = response.headers.get(self.LOCATION_HEADER)
        if not location:
            raise self._fail("Keycloak did not return the address of the new resource.")
        return location.rstrip(self.PATH_SEPARATOR).rsplit(self.PATH_SEPARATOR, 1)[-1]

    async def _token(self) -> str:
        """Get a service-account token with the client credentials.

        Returns:
            str: The access token.

        Raises:
            SEKeycloakUnreachableError: When the secret entry is missing, or the token cannot be obtained.
        """
        secret = environ.get(self.config.client_secret_key)
        if not secret:
            self.logger.debug("The secret entry %s is not set.", self.config.client_secret_key)
            raise self._fail("The secret of the Keycloak admin client is not set.")
        url = f"{self.config.server_url}{self.TOKEN_PATH.format(realm=self.config.realm)}"
        form = {
            self.GRANT_TYPE_KEY: self.CLIENT_CREDENTIALS,
            self.CLIENT_ID_KEY: self.config.client_id,
            self.CLIENT_SECRET_KEY: secret,
        }
        try:
            async with httpx.AsyncClient(timeout=self.config.request_timeout_s) as http:
                response = await http.post(url, data=form)
            if response.status_code != httpx.codes.OK:
                self.logger.debug("The token endpoint answered %d.", response.status_code)
                raise ValueError("The token endpoint refused the credentials.")
            token = str(response.json()[self.ACCESS_TOKEN_KEY])
        except (httpx.HTTPError, ValueError, KeyError, TypeError) as error:
            raise self._fail("A Keycloak token could not be obtained.", error) from error
        self.logger.debug("Got a Keycloak token.")
        return token

    async def _send(
        self,
        method: str,
        path: str,
        token: str,
        body: Optional[JsonValue] = None,
        params: Optional[Dict[str, str]] = None,
        conflict_possible: bool = False,
    ) -> httpx.Response:
        """Send one request to the admin API.

        Args:
            method (str): The HTTP method.
            path (str): The path below the admin API of the realm.
            token (str): The access token.
            body (Optional[JsonValue]): The JSON body, when there is one.
            params (Optional[Dict[str, str]]): The query parameters, when there are some.
            conflict_possible (bool): Whether a 409 means that the resource exists already.

        Returns:
            httpx.Response: The successful answer.

        Raises:
            SEKeycloakConflictError: When ``conflict_possible`` and Keycloak answers 409.
            SEKeycloakUnreachableError: When the call fails or Keycloak answers an error.
        """
        headers = {self.AUTHORIZATION_HEADER: self.BEARER_PREFIX + token}
        try:
            async with httpx.AsyncClient(timeout=self.config.request_timeout_s) as http:
                response = await http.request(method, self._admin_url(path), headers=headers, json=body, params=params)
        except httpx.HTTPError as error:
            raise self._fail("Keycloak could not be reached.", error) from error
        if response.status_code == httpx.codes.CONFLICT and conflict_possible:
            self.logger.error("Keycloak answered 409 on %s %s.", method, path)
            raise SEKeycloakConflictError("The resource exists already in Keycloak.")
        if not response.is_success:
            raise self._fail(f"Keycloak answered {response.status_code} on {method} {path}.")
        self.logger.debug("Keycloak answered %d on %s %s.", response.status_code, method, path)
        return response

    async def _complete_invitation(
        self, organisation_id: str, user_id: str, token: str, required_actions: List[JsonValue]
    ) -> None:
        """Give the new user their role, add them to the organisation and send the actions e-mail.

        Args:
            organisation_id (str): The organisation of their Operator.
            user_id (str): The new user.
            token (str): The access token.
            required_actions (List[JsonValue]): The actions the person must do at the first sign-in.

        Raises:
            SEKeycloakUnreachableError: When Keycloak cannot be reached or refuses.
        """
        role_name = RoleName.MISSION_PLANNER.value
        role = await self._send(self.GET, f"{self.ROLES_PATH}/{role_name}", token)
        await self._send(self.POST, f"{self.USERS_PATH}/{user_id}{self.ROLE_MAPPINGS_SUFFIX}", token, [role.json()])
        await self._send(self.POST, f"{self.ORGANISATIONS_PATH}/{organisation_id}{self.MEMBERS_SUFFIX}", token, user_id)
        await self._send(
            self.PUT,
            f"{self.USERS_PATH}/{user_id}{self.ACTIONS_EMAIL_SUFFIX}",
            token,
            required_actions,
            {self.CLIENT_ID_KEY: self.config.sign_in_client_id},
        )

    async def _delete_user_quietly(self, user_id: str) -> None:
        """Delete a user as a clean-up, and only warn when that fails.

        Args:
            user_id (str): The user to delete.
        """
        try:
            await self.delete_user(user_id)
        except SEKeycloakUnreachableError as error:
            self.logger.warning("The Keycloak user %s could not be deleted: %s.", user_id, type(error).__name__)
        else:
            self.logger.debug("Deleted the Keycloak user %s after a failed invitation.", user_id)

    ############################
    # Publicly Exposed Methods #
    ############################

    async def create_organisation(self, operator: Operator) -> str:
        """Create the organisation of an Operator.

        Args:
            operator (Operator): The Operator, whose name and identifier the organisation holds.

        Returns:
            str: The identifier of the organisation.

        Raises:
            SEKeycloakUnreachableError: When Keycloak cannot be reached or refuses.
        """
        token = await self._token()
        body: Dict[str, JsonValue] = {
            self.NAME_KEY: operator.name,
            self.ALIAS_KEY: str(operator.id),
            self.ATTRIBUTES_KEY: {self.OPERATOR_ID_ATTRIBUTE: [str(operator.id)]},
        }
        response = await self._send(self.POST, self.ORGANISATIONS_PATH, token, body)
        identifier = self._created_id(response)
        self.logger.info("Created the Keycloak organisation %s.", identifier)
        return identifier

    async def invite_mission_planner(self, organisation_id: str, person: Person) -> str:
        """Create a Mission planner, add them to an organisation and send them the actions e-mail.

        Args:
            organisation_id (str): The organisation of their Operator.
            person (Person): The person to invite.

        Returns:
            str: The identifier of the user.

        Raises:
            SEKeycloakConflictError: When the e-mail address is used already.
            SEKeycloakUnreachableError: When Keycloak cannot be reached or refuses.
        """
        token = await self._token()
        attributes: Dict[str, JsonValue] = {self.OPERATOR_ID_ATTRIBUTE: [str(person.operator_id)]}
        required_actions: List[JsonValue] = list(self.REQUIRED_ACTIONS)
        user: Dict[str, JsonValue] = {
            self.USERNAME_KEY: person.email,
            self.EMAIL_KEY: person.email,
            self.FIRST_NAME_KEY: person.name,
            self.ENABLED_KEY: True,
            self.ATTRIBUTES_KEY: attributes,
            self.REQUIRED_ACTIONS_KEY: required_actions,
        }
        response = await self._send(self.POST, self.USERS_PATH, token, user, conflict_possible=True)
        user_id = self._created_id(response)
        try:
            await self._complete_invitation(organisation_id, user_id, token, required_actions)
        except SEKeycloakUnreachableError:
            self.logger.error("A step after creating the Keycloak user %s failed, so the user is deleted.", user_id)
            await self._delete_user_quietly(user_id)
            raise
        self.logger.info("Invited a Mission planner as the Keycloak user %s.", user_id)
        return user_id

    async def delete_organisation(self, organisation_id: str) -> None:
        """Delete an organisation.

        Args:
            organisation_id (str): The organisation to delete.

        Raises:
            SEKeycloakUnreachableError: When Keycloak cannot be reached or refuses.
        """
        token = await self._token()
        await self._send(self.DELETE, f"{self.ORGANISATIONS_PATH}/{organisation_id}", token)
        self.logger.info("Deleted the Keycloak organisation %s.", organisation_id)

    async def delete_user(self, user_id: str) -> None:
        """Delete a user.

        Args:
            user_id (str): The user to delete.

        Raises:
            SEKeycloakUnreachableError: When Keycloak cannot be reached or refuses.
        """
        token = await self._token()
        await self._send(self.DELETE, f"{self.USERS_PATH}/{user_id}", token)
        self.logger.info("Deleted the Keycloak user %s.", user_id)
