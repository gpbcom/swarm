from __future__ import annotations

# Standard library imports
from typing import List

# First-party imports
from swarm_live.service.live_hub import LiveHub  # isort: skip


class TestLiveHub:
    def test_the_first_watcher_of_a_key_is_reported(self) -> None:
        hub = LiveHub()
        _, first = hub.subscribe("topic-a")
        _, second = hub.subscribe("topic-a")
        assert first is True
        assert second is False
        assert hub.watchers("topic-a") == 2

    def test_the_last_watcher_to_leave_is_reported(self) -> None:
        hub = LiveHub()
        mailbox_one, _ = hub.subscribe("topic-a")
        mailbox_two, _ = hub.subscribe("topic-a")
        assert hub.unsubscribe("topic-a", mailbox_one) is False
        assert hub.unsubscribe("topic-a", mailbox_two) is True
        assert hub.watchers("topic-a") == 0

    def test_a_publish_to_a_key_with_no_watcher_reaches_nobody(self) -> None:
        assert LiveHub().publish("nobody", b"frame") == 0

    def test_a_publish_reaches_every_watcher_of_its_key_only(self) -> None:
        hub = LiveHub()
        mailbox_a1, _ = hub.subscribe("topic-a")
        mailbox_a2, _ = hub.subscribe("topic-a")
        mailbox_b, _ = hub.subscribe("topic-b")
        assert hub.publish("topic-a", b"frame") == 2
        assert mailbox_a1.pending() is True
        assert mailbox_a2.pending() is True
        assert mailbox_b.pending() is False

    def test_a_publish_after_an_unsubscribe_no_longer_reaches_the_mailbox(self) -> None:
        hub = LiveHub()
        mailbox, _ = hub.subscribe("topic-a")
        hub.unsubscribe("topic-a", mailbox)
        assert hub.publish("topic-a", b"frame") == 0
        assert mailbox.pending() is False

    def test_each_watcher_has_its_own_mailbox(self) -> None:
        hub = LiveHub()
        mailbox_one, _ = hub.subscribe("topic-a")
        mailbox_two, _ = hub.subscribe("topic-a")
        assert mailbox_one is not mailbox_two

    def test_a_key_that_was_emptied_reports_a_first_watcher_again(self) -> None:
        hub = LiveHub()
        mailbox, _ = hub.subscribe("topic-a")
        hub.unsubscribe("topic-a", mailbox)
        _, first = hub.subscribe("topic-a")
        assert first is True

    async def test_a_slow_watcher_skips_frames_while_a_fast_one_gets_each(self) -> None:
        hub = LiveHub()
        slow, _ = hub.subscribe("topic-a")
        fast, _ = hub.subscribe("topic-a")
        received: List[bytes] = []
        for index in range(5):
            hub.publish("topic-a", str(index).encode())
            received.append(await fast.take())
        assert received == [b"0", b"1", b"2", b"3", b"4"]
        assert await slow.take() == b"4"
        assert slow.skipped == 4
        assert fast.skipped == 0
