from __future__ import annotations

# Standard library imports
from typing import Dict, List, Optional
from uuid import UUID

# Third-party imports
from pydantic import JsonValue

# First-party imports
from swarm_models.people.enums import RoleName

AUDIENCE = "swarm-gateway"
REALM_PATH = "/realms/swarm"
CERTS_PATH = REALM_PATH + "/protocol/openid-connect/certs"
SUB_KEY = "sub"
ISS_KEY = "iss"
AUD_KEY = "aud"
REALM_ACCESS_KEY = "realm_access"
ROLES_KEY = "roles"
OPERATOR_ID_KEY = "operator_id"


def claims_for(
    issuer_url: str,
    person_id: UUID,
    operator_id: Optional[UUID],
    roles: List[RoleName],
    audience: str = AUDIENCE,
) -> Dict[str, JsonValue]:
    claims: Dict[str, JsonValue] = {
        SUB_KEY: str(person_id),
        ISS_KEY: issuer_url,
        AUD_KEY: audience,
        REALM_ACCESS_KEY: {ROLES_KEY: [role.value for role in roles]},
    }
    if operator_id is not None:
        claims[OPERATOR_ID_KEY] = str(operator_id)
    return claims


REALM = "swarm"
ADMIN_CLIENT_ID = "swarm-gateway-admin"
TOKEN_PATH = REALM_PATH + "/protocol/openid-connect/token"
ADMIN_PATH = "/admin/realms/" + REALM
ORGANISATIONS_PATH = ADMIN_PATH + "/organizations"
USERS_PATH = ADMIN_PATH + "/users"
ROLES_PATH = ADMIN_PATH + "/roles"
SECRET_ENVIRONMENT_ENTRY = "SWARM_GATEWAY_KEYCLOAK_CLIENT_SECRET"
ACCESS_TOKEN_KEY = "access_token"
TOKEN_TYPE_KEY = "token_type"
EXPIRES_IN_KEY = "expires_in"
BEARER = "Bearer"
CLIENT_ID_KEY = "client_id"
CLIENT_SECRET_KEY = "client_secret"
GRANT_TYPE_KEY = "grant_type"
CLIENT_CREDENTIALS = "client_credentials"
ID_KEY = "id"
NAME_KEY = "name"
EMAIL_KEY = "email"
USERNAME_KEY = "username"
FIRST_NAME_KEY = "firstName"
ATTRIBUTES_KEY = "attributes"
REQUIRED_ACTIONS_KEY = "requiredActions"
GET_METHOD = "GET"
POST_METHOD = "POST"
PUT_METHOD = "PUT"
DELETE_METHOD = "DELETE"
