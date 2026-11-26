from __future__ import annotations

# Standard library imports
from enum import StrEnum, unique


@unique
class AccessRefusal(StrEnum):
    """Why the gateway refused a call.

    Attributes:
        MISSING_TOKEN: The call carried no bearer token.
        INVALID_TOKEN: The token is malformed, wrongly signed or addressed to another issuer or audience.
        EXPIRED_TOKEN: The token is past its expiry.
        WRONG_OPERATOR: The token's Operator is not the Operator the call targets.
        MISSING_ROLE: The token lacks the role the call needs.
        IDENTITY_UNAVAILABLE: The identity provider could not be reached or its signing key is unknown.
    """

    MISSING_TOKEN = "missing_token"
    INVALID_TOKEN = "invalid_token"
    EXPIRED_TOKEN = "expired_token"
    WRONG_OPERATOR = "wrong_operator"
    MISSING_ROLE = "missing_role"
    IDENTITY_UNAVAILABLE = "identity_unavailable"


@unique
class TokenClaim(StrEnum):
    """The claims of an access token that the gateway reads.

    Attributes:
        SUBJECT: The subject, ``sub``.
        ISSUER: The issuer, ``iss``.
        AUDIENCE: The audience, ``aud``.
        EXPIRES_AT: The expiry time, ``exp``.
        ISSUED_AT: The issue time, ``iat``.
        OPERATOR_ID: The Operator the caller belongs to, ``operator_id``.
        REALM_ACCESS: The realm access section, ``realm_access``.
        ROLES: The list of roles inside the realm access section, ``roles``.
    """

    SUBJECT = "sub"
    ISSUER = "iss"
    AUDIENCE = "aud"
    EXPIRES_AT = "exp"
    ISSUED_AT = "iat"
    OPERATOR_ID = "operator_id"
    REALM_ACCESS = "realm_access"
    ROLES = "roles"
