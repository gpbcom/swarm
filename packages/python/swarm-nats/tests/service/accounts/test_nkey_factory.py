from __future__ import annotations

from typing import ClassVar, Dict

import pytest
from nkeys import KeyPair

# First-party imports
from swarm_nats.models.accounts.exceptions import SENkeyInvalidSeedError
from swarm_nats.models.enums import NatsClaimType
from swarm_nats.service.accounts.nkey_factory import NkeyFactory


class TestNkeyFactory:
    PUBLIC_PREFIX: ClassVar[Dict[NatsClaimType, str]] = {
        NatsClaimType.OPERATOR: "O",
        NatsClaimType.ACCOUNT: "A",
        NatsClaimType.USER: "U",
    }
    SEED_PREFIX: ClassVar[Dict[NatsClaimType, str]] = {
        NatsClaimType.OPERATOR: "SO",
        NatsClaimType.ACCOUNT: "SA",
        NatsClaimType.USER: "SU",
    }
    PUBLIC_KEY_LENGTH: ClassVar[int] = 56
    SEED_LENGTH: ClassVar[int] = 58

    @pytest.mark.parametrize("kind", [NatsClaimType.OPERATOR, NatsClaimType.ACCOUNT, NatsClaimType.USER])
    def test_the_public_key_has_the_prefix_and_length_of_its_kind(self, kind: NatsClaimType) -> None:
        factory = NkeyFactory()
        public_key = factory.public_key(factory.create(kind))
        assert public_key.startswith(self.PUBLIC_PREFIX[kind])
        assert len(public_key) == self.PUBLIC_KEY_LENGTH

    @pytest.mark.parametrize("kind", [NatsClaimType.OPERATOR, NatsClaimType.ACCOUNT, NatsClaimType.USER])
    def test_the_seed_has_the_prefix_and_length_of_its_kind(self, kind: NatsClaimType) -> None:
        factory = NkeyFactory()
        seed = factory.seed(factory.create(kind))
        assert seed.startswith(self.SEED_PREFIX[kind])
        assert len(seed) == self.SEED_LENGTH

    @pytest.mark.parametrize("kind", [NatsClaimType.OPERATOR, NatsClaimType.ACCOUNT, NatsClaimType.USER])
    def test_a_seed_gives_back_the_same_public_key(self, kind: NatsClaimType) -> None:
        factory = NkeyFactory()
        pair = factory.create(kind)
        restored = factory.from_seed(factory.seed(pair))
        assert isinstance(restored, KeyPair)
        assert factory.public_key(restored) == factory.public_key(pair)

    @pytest.mark.parametrize("kind", [NatsClaimType.OPERATOR, NatsClaimType.ACCOUNT, NatsClaimType.USER])
    def test_two_creations_give_different_keys(self, kind: NatsClaimType) -> None:
        factory = NkeyFactory()
        first = factory.create(kind)
        second = factory.create(kind)
        assert factory.public_key(first) != factory.public_key(second)
        assert factory.seed(first) != factory.seed(second)

    @pytest.mark.parametrize("seed", ["", "not a seed", "SUAAAA", "A" * 58])
    def test_a_malformed_seed_is_refused(self, seed: str) -> None:
        with pytest.raises(SENkeyInvalidSeedError):
            NkeyFactory().from_seed(seed)
