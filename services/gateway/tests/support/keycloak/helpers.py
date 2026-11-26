from __future__ import annotations

# Standard library imports
from typing import Dict, List, Optional
from uuid import UUID

# Third-party imports
from pydantic import JsonValue

# First-party imports
from swarm_models.models.people.enums import RoleName

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
