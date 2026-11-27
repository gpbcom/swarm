from __future__ import annotations

# Standard library imports
from typing import Dict, List, Optional
from uuid import UUID, uuid4

# Third-party imports
from pydantic import JsonValue

# First-party imports
from swarm_models.enums import Anchoring, Deployment, Jurisdiction, LlmProvider
from swarm_models.people.enums import RoleName
from tests.fakes.keycloak.helpers import claims_for
from tests.fakes.keycloak.keycloak_stand_in import KeycloakStandIn

SCHEMA = "gateway"
CREATE_SCHEMA = "CREATE SCHEMA gateway"
OPERATORS_PATH = "/v1/operators"
OPERATOR_PATH_TEMPLATE = "/v1/operators/{operator_id}"
AUTHORIZATION = "Authorization"
BEARER_TEMPLATE = "Bearer {token}"
IDEMPOTENCY_KEY = "Idempotency-Key"
CONTENT_TYPE = "content-type"
BASE_URL = "http://gateway"
KEYCLOAK_FIELD = "keycloak"
SERVER_URL_FIELD = "server_url"
OPERATORS_FIELD = "operators"
OPERATOR_FIELD = "operator"
CELL_ASSIGNMENT_FIELD = "cell_assignment"
FIRST_MISSION_PLANNER_FIELD = "first_mission_planner"
ID_FIELD = "id"
NAME_FIELD = "name"
EMAIL_FIELD = "email"
OPERATOR_ID_FIELD = "operator_id"
DETAIL_FIELD = "detail"
OPERATOR_ID_ATTRIBUTE = "operator_id"
ATTRIBUTES_FIELD = "attributes"
AEROWING_NAME = "Aerowing Services"
AEROWING_PLANNER_NAME = "Camille Laurent"
AEROWING_PLANNER_EMAIL = "camille.laurent@aerowing.example"
SKYLINE_NAME = "Skyline Survey"
SKYLINE_PLANNER_NAME = "Jonas Weber"
SKYLINE_PLANNER_EMAIL = "jonas.weber@skyline.example"
MISSING_OPERATOR = UUID("01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e7f")
ADMINISTRATOR_ID = UUID("01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e01")
OUTSIDER_ID = UUID("01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e02")
OUTSIDER_OPERATOR_ID = UUID("01943c5e-8a4b-7c2d-9e1f-0a1b2c3d4e03")


def bearer(token: str) -> Dict[str, str]:
    return {AUTHORIZATION: BEARER_TEMPLATE.format(token=token)}


def post_headers(token: str, key: Optional[str] = None) -> Dict[str, str]:
    return {**bearer(token), IDEMPOTENCY_KEY: key if key else uuid4().hex}


def mint(stand_in: KeycloakStandIn, person_id: UUID, operator_id: Optional[UUID], role: RoleName) -> str:
    return stand_in.mint(claims_for(stand_in.issuer_url, person_id, operator_id, [role]))


def entry_body(
    name: Optional[str],
    planner_name: str,
    planner_email: str,
    jurisdictions: Optional[List[Jurisdiction]] = None,
) -> Dict[str, JsonValue]:
    chosen = jurisdictions if jurisdictions is not None else [Jurisdiction.EU_EASA]
    body: Dict[str, JsonValue] = {
        "name": name,
        "deployment": Deployment.CLOUD.value,
        "jurisdictions": [jurisdiction.value for jurisdiction in chosen],
        "llm_provider": LlmProvider.CLAUDE.value,
        "anchoring": Anchoring.QUALIFIED_TIMESTAMPING.value,
        "first_mission_planner_name": planner_name,
        "first_mission_planner_email": planner_email,
    }
    return body


def aerowing_body(jurisdictions: Optional[List[Jurisdiction]] = None) -> Dict[str, JsonValue]:
    return entry_body(AEROWING_NAME, AEROWING_PLANNER_NAME, AEROWING_PLANNER_EMAIL, jurisdictions)


def skyline_body() -> Dict[str, JsonValue]:
    return entry_body(SKYLINE_NAME, SKYLINE_PLANNER_NAME, SKYLINE_PLANNER_EMAIL)
