from __future__ import annotations

# Standard library imports
import json
import secrets
import threading
from http.server import ThreadingHTTPServer
from types import TracebackType
from typing import ClassVar, Dict, List, Optional, Self, Set, Tuple, Type
from urllib.parse import parse_qs
from uuid import uuid4

# Third-party imports
from pydantic import JsonValue

# First-party imports
from swarm_models.people.enums import RoleName
from tests.fakes.keycloak.admin_request_handler import AdminRequestHandler
from tests.fakes.keycloak.helpers import (
    ACCESS_TOKEN_KEY,
    ADMIN_CLIENT_ID,
    BEARER,
    CLIENT_CREDENTIALS,
    CLIENT_ID_KEY,
    CLIENT_SECRET_KEY,
    DELETE_METHOD,
    EMAIL_KEY,
    EXPIRES_IN_KEY,
    GET_METHOD,
    GRANT_TYPE_KEY,
    ID_KEY,
    NAME_KEY,
    ORGANISATIONS_PATH,
    POST_METHOD,
    PUT_METHOD,
    REALM,
    ROLES_PATH,
    TOKEN_PATH,
    TOKEN_TYPE_KEY,
    USERNAME_KEY,
    USERS_PATH,
)


class KeycloakAdminStandIn:
    """A local stand-in for the admin REST API of Keycloak, recording what it is asked to hold.

    Attributes:
        realm (str): The realm it serves.
        client_id (str): The service-account client it accepts.
        client_secret (str): The random secret of that client.
        organisations (Dict[str, Dict[str, JsonValue]]): The organisations, by identifier.
        users (Dict[str, Dict[str, JsonValue]]): The users, by identifier.
        realm_roles (Dict[str, List[str]]): The realm role names of each user, by user identifier.
        members (Dict[str, List[str]]): The user identifiers of each organisation, by organisation identifier.
        action_emails (List[Tuple[str, List[str], str]]): The actions e-mails sent, as user, actions and client.
        token_requests (int): How many tokens were asked for.
        HOST (str): The address the server listens on.
        ENCODING (str): The encoding of the bodies.
        TOKEN_LIFETIME_S (int): The lifetime of a token it issues.
        SECRET_BYTES (int): The size of the random secret.

    Notes:
        - Every path answers only with the bearer token it issued for the right secret.
        - ``fail_path`` makes the next request whose path contains the fragment answer 500.
    """

    HOST: ClassVar[str] = "127.0.0.1"
    ENCODING: ClassVar[str] = "utf-8"
    TOKEN_LIFETIME_S: ClassVar[int] = 300
    SECRET_BYTES: ClassVar[int] = 16
    BEARER_PREFIX: ClassVar[str] = BEARER + " "
    MEMBERS_SUFFIX: ClassVar[str] = "/members"
    ROLE_MAPPINGS_SUFFIX: ClassVar[str] = "/role-mappings/realm"
    ACTIONS_EMAIL_SUFFIX: ClassVar[str] = "/execute-actions-email"
    OK_STATUS: ClassVar[int] = 200
    CREATED_STATUS: ClassVar[int] = 201
    NO_CONTENT_STATUS: ClassVar[int] = 204
    UNAUTHORISED_STATUS: ClassVar[int] = 401
    NOT_FOUND_STATUS: ClassVar[int] = 404
    CONFLICT_STATUS: ClassVar[int] = 409
    FAILURE_STATUS: ClassVar[int] = 500

    def __init__(self) -> None:
        self.realm = REALM
        self.client_id = ADMIN_CLIENT_ID
        self.client_secret = secrets.token_urlsafe(self.SECRET_BYTES)
        self.organisations: Dict[str, Dict[str, JsonValue]] = {}
        self.users: Dict[str, Dict[str, JsonValue]] = {}
        self.realm_roles: Dict[str, List[str]] = {}
        self.members: Dict[str, List[str]] = {}
        self.action_emails: List[Tuple[str, List[str], str]] = []
        self.token_requests = 0
        self.tokens: Set[str] = set()
        self.failing_fragments: List[str] = []
        self.server: Optional[ThreadingHTTPServer] = None
        self.thread: Optional[threading.Thread] = None

    ############################
    # Internal Helpers Methods #
    ############################

    def json_answer(self, status: int, body: JsonValue) -> Tuple[int, Optional[str], bytes]:
        return status, None, json.dumps(body).encode(self.ENCODING)

    def empty_answer(self, status: int, location: Optional[str] = None) -> Tuple[int, Optional[str], bytes]:
        return status, location, b""

    def token_answer(self, body: bytes) -> Tuple[int, Optional[str], bytes]:
        form = parse_qs(body.decode(self.ENCODING))
        given_id = form.get(CLIENT_ID_KEY, [""])[0]
        given_secret = form.get(CLIENT_SECRET_KEY, [""])[0]
        grant = form.get(GRANT_TYPE_KEY, [""])[0]
        if (
            grant != CLIENT_CREDENTIALS
            or given_id != self.client_id
            or not secrets.compare_digest(given_secret, self.client_secret)
        ):
            return self.empty_answer(self.UNAUTHORISED_STATUS)
        self.token_requests += 1
        token = secrets.token_urlsafe(self.SECRET_BYTES)
        self.tokens.add(token)
        return self.json_answer(
            self.OK_STATUS,
            {ACCESS_TOKEN_KEY: token, TOKEN_TYPE_KEY: BEARER, EXPIRES_IN_KEY: self.TOKEN_LIFETIME_S},
        )

    def is_authorised(self, authorization: Optional[str]) -> bool:
        if authorization is None or not authorization.startswith(self.BEARER_PREFIX):
            return False
        return authorization[len(self.BEARER_PREFIX) :] in self.tokens

    def parse_json(self, body: bytes) -> JsonValue:
        parsed: JsonValue = json.loads(body.decode(self.ENCODING)) if body else None
        return parsed

    def email_is_used(self, address: str) -> bool:
        return any(str(user.get(EMAIL_KEY, "")).lower() == address.lower() for user in self.users.values())

    def create_answer(self, path: str, body: bytes) -> Tuple[int, Optional[str], bytes]:
        parsed = self.parse_json(body)
        if not isinstance(parsed, dict):
            return self.empty_answer(self.FAILURE_STATUS)
        identifier = str(uuid4())
        location = f"{self.server_url}{path}/{identifier}"
        if path == ORGANISATIONS_PATH:
            self.organisations[identifier] = {**parsed, ID_KEY: identifier}
            return self.empty_answer(self.CREATED_STATUS, location)
        email = parsed.get(EMAIL_KEY)
        if isinstance(email, str) and self.email_is_used(email):
            return self.empty_answer(self.CONFLICT_STATUS)
        self.users[identifier] = {**parsed, ID_KEY: identifier}
        return self.empty_answer(self.CREATED_STATUS, location)

    def delete_answer(self, path: str) -> Tuple[int, Optional[str], bytes]:
        for prefix, store in ((ORGANISATIONS_PATH, self.organisations), (USERS_PATH, self.users)):
            if path.startswith(prefix + "/"):
                identifier = path[len(prefix) + 1 :]
                if identifier not in store:
                    return self.empty_answer(self.NOT_FOUND_STATUS)
                del store[identifier]
                return self.empty_answer(self.NO_CONTENT_STATUS)
        return self.empty_answer(self.NOT_FOUND_STATUS)

    def role_answer(self, path: str) -> Tuple[int, Optional[str], bytes]:
        name = path[len(ROLES_PATH) + 1 :]
        if name not in {role.value for role in RoleName}:
            return self.empty_answer(self.NOT_FOUND_STATUS)
        return self.json_answer(self.OK_STATUS, {ID_KEY: name, NAME_KEY: name})

    def role_mapping_answer(self, path: str, body: bytes) -> Tuple[int, Optional[str], bytes]:
        user_id = path[len(USERS_PATH) + 1 : -len(self.ROLE_MAPPINGS_SUFFIX)]
        parsed = self.parse_json(body)
        if user_id not in self.users or not isinstance(parsed, list):
            return self.empty_answer(self.NOT_FOUND_STATUS)
        names = [str(role[NAME_KEY]) for role in parsed if isinstance(role, dict) and NAME_KEY in role]
        self.realm_roles.setdefault(user_id, []).extend(names)
        return self.empty_answer(self.NO_CONTENT_STATUS)

    def member_answer(self, path: str, body: bytes) -> Tuple[int, Optional[str], bytes]:
        organisation_id = path[len(ORGANISATIONS_PATH) + 1 : -len(self.MEMBERS_SUFFIX)]
        user_id = body.decode(self.ENCODING).strip().strip('"')
        if organisation_id not in self.organisations or user_id not in self.users:
            return self.empty_answer(self.NOT_FOUND_STATUS)
        self.members.setdefault(organisation_id, []).append(user_id)
        return self.empty_answer(self.CREATED_STATUS)

    def actions_email_answer(self, path: str, query: str, body: bytes) -> Tuple[int, Optional[str], bytes]:
        user_id = path[len(USERS_PATH) + 1 : -len(self.ACTIONS_EMAIL_SUFFIX)]
        parsed = self.parse_json(body)
        client_id = parse_qs(query).get(CLIENT_ID_KEY, [""])[0]
        if user_id not in self.users or not isinstance(parsed, list):
            return self.empty_answer(self.NOT_FOUND_STATUS)
        self.action_emails.append((user_id, [str(action) for action in parsed], client_id))
        return self.empty_answer(self.NO_CONTENT_STATUS)

    ############################
    # Publicly Exposed Methods #
    ############################

    def __enter__(self) -> Self:
        server = ThreadingHTTPServer((self.HOST, 0), AdminRequestHandler)
        server.stand_in = self  # type: ignore[attr-defined]
        self.server = server
        self.thread = threading.Thread(target=server.serve_forever, daemon=True)
        self.thread.start()
        return self

    def __exit__(
        self,
        error_type: Optional[Type[BaseException]],
        error: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        if self.server is not None:
            self.server.shutdown()
            self.server.server_close()
        if self.thread is not None:
            self.thread.join()

    @property
    def server_url(self) -> str:
        assert self.server is not None
        return f"http://{self.HOST}:{self.server.server_address[1]}"

    def fail_path(self, fragment: str) -> None:
        self.failing_fragments.append(fragment)

    def existing_email(self, address: str) -> str:
        identifier = str(uuid4())
        self.users[identifier] = {ID_KEY: identifier, EMAIL_KEY: address, USERNAME_KEY: address}
        return identifier

    def respond(
        self, method: str, path: str, query: str, authorization: Optional[str], body: bytes
    ) -> Tuple[int, Optional[str], bytes]:
        for fragment in self.failing_fragments:
            if fragment in path:
                self.failing_fragments.remove(fragment)
                return self.empty_answer(self.FAILURE_STATUS)
        if path == TOKEN_PATH:
            return self.token_answer(body)
        if not self.is_authorised(authorization):
            return self.empty_answer(self.UNAUTHORISED_STATUS)
        if method == POST_METHOD and path in (ORGANISATIONS_PATH, USERS_PATH):
            return self.create_answer(path, body)
        if method == POST_METHOD and path.startswith(ORGANISATIONS_PATH) and path.endswith(self.MEMBERS_SUFFIX):
            return self.member_answer(path, body)
        if method == POST_METHOD and path.startswith(USERS_PATH) and path.endswith(self.ROLE_MAPPINGS_SUFFIX):
            return self.role_mapping_answer(path, body)
        if method == PUT_METHOD and path.startswith(USERS_PATH) and path.endswith(self.ACTIONS_EMAIL_SUFFIX):
            return self.actions_email_answer(path, query, body)
        if method == GET_METHOD and path.startswith(ROLES_PATH + "/"):
            return self.role_answer(path)
        if method == DELETE_METHOD:
            return self.delete_answer(path)
        return self.empty_answer(self.NOT_FOUND_STATUS)
