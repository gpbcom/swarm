from __future__ import annotations

# Standard library imports
import json
from pathlib import Path
from typing import ClassVar, Dict, List, Set, cast

# Third-party imports
import pytest
from pydantic import JsonValue

# First-party imports
from swarm_models.models.people.enums import RoleName


class TestSwarmRealm:
    ROOT: ClassVar[Path] = Path(__file__).resolve().parents[4]
    REALM_FILE: ClassVar[Path] = ROOT / "deploy" / "charts" / "keycloak" / "files" / "swarm-realm.json"
    ENCODING: ClassVar[str] = "utf-8"
    REALM_NAME: ClassVar[str] = "swarm"
    KEYCLOAK_ROLES: ClassVar[Set[str]] = {"offline_access", "uma_authorization", "default-roles-swarm"}
    ACCESS_TOKEN_SECONDS: ClassVar[int] = 300
    CLIENT_IDS: ClassVar[Set[str]] = {"ground-control", "mission-studio", "back-office", "client-portal", "desktop"}
    CLIENT_SCOPES: ClassVar[Set[str]] = {"swarm", "roles", "basic"}
    PKCE_ATTRIBUTE: ClassVar[str] = "pkce.code.challenge.method"
    PKCE_METHOD: ClassVar[str] = "S256"
    BROWSER_FLOW: ClassVar[str] = "swarm browser"
    OIDC: ClassVar[str] = "openid-connect"
    ATTRIBUTE_MAPPER: ClassVar[str] = "oidc-usermodel-attribute-mapper"
    AUDIENCE_MAPPER: ClassVar[str] = "oidc-audience-mapper"
    ROLE_CONDITION: ClassVar[str] = "conditional-user-role"
    OTP_FORM: ClassVar[str] = "auth-otp-form"
    PASSWORD_FORM: ClassVar[str] = "auth-username-password-form"
    REQUIRED: ClassVar[str] = "REQUIRED"
    CONDITIONAL: ClassVar[str] = "CONDITIONAL"
    ROLES_CLAIM: ClassVar[str] = "realm_access.roles"
    SUBJECT_CLAIM: ClassVar[str] = "sub"
    OPERATOR_CLAIM: ClassVar[str] = "operator_id"
    GATEWAY_AUDIENCE: ClassVar[str] = "swarm-gateway"
    TOTP: ClassVar[str] = "totp"
    CONFIGURE_TOTP: ClassVar[str] = "CONFIGURE_TOTP"
    MFA_ROLES: ClassVar[Set[str]] = {
        RoleName.PILOT.value,
        RoleName.MISSION_PLANNER.value,
        RoleName.FLEET_MAINTAINER.value,
        RoleName.INSTRUCTOR.value,
        RoleName.SWARM_ADMINISTRATOR.value,
    }
    FORBIDDEN_KEYS: ClassVar[Set[str]] = {"password", "secret"}
    PROFILE_PROVIDER: ClassVar[str] = "org.keycloak.userprofile.UserProfileProvider"
    PROFILE_CONFIG: ClassVar[str] = "kc.user.profile.config"
    UNMANAGED_POLICY: ClassVar[str] = "unmanagedAttributePolicy"
    ADMIN_ONLY: ClassVar[List[str]] = ["admin"]

    def _realm(self) -> Dict[str, JsonValue]:
        loaded = json.loads(self.REALM_FILE.read_text(encoding=self.ENCODING))
        assert isinstance(loaded, dict)
        return cast(Dict[str, JsonValue], loaded)

    def _items(self, value: JsonValue) -> List[Dict[str, JsonValue]]:
        assert isinstance(value, list)
        for item in value:
            assert isinstance(item, dict)
        return cast(List[Dict[str, JsonValue]], value)

    def _section(self, value: JsonValue) -> Dict[str, JsonValue]:
        assert isinstance(value, dict)
        return cast(Dict[str, JsonValue], value)

    def _clients(self) -> List[Dict[str, JsonValue]]:
        swarm = [c for c in self._items(self._realm()["clients"]) if c["clientId"] in self.CLIENT_IDS]
        assert {c["clientId"] for c in swarm} == self.CLIENT_IDS
        return swarm

    def _scope(self, name: str) -> Dict[str, JsonValue]:
        found = [s for s in self._items(self._realm()["clientScopes"]) if s["name"] == name]
        assert len(found) == 1
        return found[0]

    def _mappers(self, scope: Dict[str, JsonValue], mapper_type: str) -> List[Dict[str, JsonValue]]:
        return [m for m in self._items(scope["protocolMappers"]) if m["protocolMapper"] == mapper_type]

    def _flow(self, alias: str) -> Dict[str, JsonValue]:
        found = [f for f in self._items(self._realm()["authenticationFlows"]) if f["alias"] == alias]
        assert len(found) == 1
        return found[0]

    def _sub_flows(self, alias: str) -> List[Dict[str, JsonValue]]:
        flow = self._flow(alias)
        reached = [flow]
        for execution in self._items(flow["authenticationExecutions"]):
            if execution.get("authenticatorFlow") is True:
                reached.extend(self._sub_flows(cast(str, execution["flowAlias"])))
        return reached

    def _role_of(self, execution: Dict[str, JsonValue]) -> str:
        alias = execution["authenticatorConfig"]
        configs = [c for c in self._items(self._realm()["authenticatorConfig"]) if c["alias"] == alias]
        assert len(configs) == 1
        return cast(str, self._section(configs[0]["config"])["condUserRole"])

    def _mfa_roles(self) -> Set[str]:
        flows = self._sub_flows(self.BROWSER_FLOW)
        conditional = {
            cast(str, execution["flowAlias"])
            for parent in flows
            for execution in self._items(parent["authenticationExecutions"])
            if execution.get("authenticatorFlow") is True and execution["requirement"] == self.CONDITIONAL
        }
        roles: Set[str] = set()
        for flow in flows:
            if flow["alias"] not in conditional:
                continue
            inner = {cast(str, e.get("authenticator")): e for e in self._items(flow["authenticationExecutions"])}
            condition = inner.get(self.ROLE_CONDITION)
            otp = inner.get(self.OTP_FORM)
            if condition is None or otp is None:
                continue
            if condition["requirement"] == self.REQUIRED and otp["requirement"] == self.REQUIRED:
                roles.add(self._role_of(condition))
        return roles

    def _keys(self, value: JsonValue) -> Set[str]:
        keys: Set[str] = set()
        if isinstance(value, dict):
            for key, inner in value.items():
                keys.add(key)
                keys |= self._keys(inner)
        elif isinstance(value, list):
            for item in value:
                keys |= self._keys(item)
        return keys

    def _profile(self) -> Dict[str, JsonValue]:
        components = self._section(self._realm().get("components", {}))
        providers = self._items(components.get(self.PROFILE_PROVIDER, []))
        assert len(providers) == 1
        configs = self._list(self._section(providers[0]["config"])[self.PROFILE_CONFIG])
        assert len(configs) == 1
        loaded = json.loads(cast(str, configs[0]))
        assert isinstance(loaded, dict)
        return cast(Dict[str, JsonValue], loaded)

    def _list(self, value: JsonValue) -> List[JsonValue]:
        assert isinstance(value, list)
        return value

    def test_the_realm_is_swarm_with_organisations(self) -> None:
        realm = self._realm()
        assert realm["realm"] == self.REALM_NAME
        assert realm["enabled"] is True
        assert realm["organizationsEnabled"] is True

    def test_the_realm_roles_are_the_roles_of_the_shared_model(self) -> None:
        names = {cast(str, r["name"]) for r in self._items(self._section(self._realm()["roles"])["realm"])}
        assert names - self.KEYCLOAK_ROLES == {role.value for role in RoleName}

    def test_access_tokens_last_five_minutes_and_refresh_tokens_rotate(self) -> None:
        realm = self._realm()
        assert realm["accessTokenLifespan"] == self.ACCESS_TOKEN_SECONDS
        assert realm["revokeRefreshToken"] is True
        assert realm["refreshTokenMaxReuse"] == 0

    def test_the_swarm_clients_are_the_five_front_ends(self) -> None:
        assert {c["clientId"] for c in self._clients()} == self.CLIENT_IDS

    @pytest.mark.parametrize(
        ("field", "expected"),
        [
            ("publicClient", True),
            ("standardFlowEnabled", True),
            ("implicitFlowEnabled", False),
            ("directAccessGrantsEnabled", False),
            ("serviceAccountsEnabled", False),
        ],
    )
    def test_every_client_is_a_public_code_flow_client(self, field: str, expected: bool) -> None:
        for client in self._clients():
            assert client[field] is expected

    def test_every_client_requires_pkce_s256(self) -> None:
        for client in self._clients():
            assert self._section(client["attributes"])[self.PKCE_ATTRIBUTE] == self.PKCE_METHOD

    def test_no_client_holds_a_secret(self) -> None:
        for client in self._clients():
            assert "secret" not in client

    def test_no_client_accepts_a_wildcard_redirect_or_origin(self) -> None:
        for client in self._clients():
            assert "*" not in self._list(client.get("redirectUris", []))
            assert "*" not in self._list(client.get("webOrigins", []))

    def test_every_client_has_the_swarm_scopes_by_default(self) -> None:
        for client in self._clients():
            assert self.CLIENT_SCOPES <= set(cast(List[str], client["defaultClientScopes"]))

    def test_the_basic_scope_puts_the_subject_in_the_token(self) -> None:
        mappers = self._items(self._scope("basic")["protocolMappers"])
        claims = [self._section(m["config"]).get("claim.name") for m in mappers]
        assert self.SUBJECT_CLAIM in claims

    def test_the_roles_scope_puts_realm_roles_in_the_access_token(self) -> None:
        mappers = self._items(self._scope("roles")["protocolMappers"])
        found = [
            m
            for m in mappers
            if self._section(m["config"]).get("claim.name") == self.ROLES_CLAIM
            and self._section(m["config"]).get("access.token.claim") == "true"
        ]
        assert len(found) == 1

    def test_the_swarm_scope_carries_the_operator_and_the_gateway_audience(self) -> None:
        scope = self._scope("swarm")
        assert scope["protocol"] == self.OIDC
        attribute = self._mappers(scope, self.ATTRIBUTE_MAPPER)
        assert len(attribute) == 1
        config = self._section(attribute[0]["config"])
        assert config["user.attribute"] == self.OPERATOR_CLAIM
        assert config["claim.name"] == self.OPERATOR_CLAIM
        assert config["jsonType.label"] == "String"
        assert config["access.token.claim"] == "true"
        audience = self._mappers(scope, self.AUDIENCE_MAPPER)
        assert len(audience) == 1
        audience_config = self._section(audience[0]["config"])
        assert audience_config["included.custom.audience"] == self.GATEWAY_AUDIENCE
        assert audience_config["access.token.claim"] == "true"

    def test_the_browser_flow_is_the_swarm_flow_and_asks_for_a_password(self) -> None:
        assert self._realm()["browserFlow"] == self.BROWSER_FLOW
        authenticators = {
            e.get("authenticator")
            for flow in self._sub_flows(self.BROWSER_FLOW)
            for e in self._items(flow["authenticationExecutions"])
        }
        assert self.PASSWORD_FORM in authenticators

    def test_only_the_five_staff_roles_must_use_a_second_factor(self) -> None:
        roles = self._mfa_roles()
        assert roles == self.MFA_ROLES
        assert RoleName.CLIENT.value not in roles
        assert RoleName.SITE_AGENT.value not in roles

    def test_totp_is_the_second_factor_and_can_be_configured(self) -> None:
        realm = self._realm()
        assert realm["otpPolicyType"] == self.TOTP
        actions = [a for a in self._items(realm["requiredActions"]) if a["alias"] == self.CONFIGURE_TOTP]
        assert len(actions) == 1
        assert actions[0]["enabled"] is True

    def test_the_realm_holds_no_user_and_no_secret(self) -> None:
        realm = self._realm()
        assert not realm.get("users")
        assert not (self._keys(realm) & self.FORBIDDEN_KEYS)

    def test_the_operator_attribute_is_declared_and_only_an_administrator_can_see_or_change_it(self) -> None:
        profile = self._profile()
        declared = [a for a in self._items(profile["attributes"]) if a["name"] == self.OPERATOR_CLAIM]
        assert len(declared) == 1
        permissions = self._section(declared[0]["permissions"])
        assert permissions["view"] == self.ADMIN_ONLY
        assert permissions["edit"] == self.ADMIN_ONLY

    def test_unmanaged_attributes_stay_off(self) -> None:
        assert self.UNMANAGED_POLICY not in self._profile()
