from __future__ import annotations

# Standard library imports
import asyncio

# Third-party imports
import pytest

# First-party imports
from swarm_live.service.live_mailbox import LiveMailbox  # isort: skip


class TestLiveMailbox:
    def test_a_new_mailbox_is_empty(self) -> None:
        mailbox = LiveMailbox()
        assert mailbox.pending() is False
        assert mailbox.skipped == 0
        assert mailbox.delivered == 0

    async def test_one_frame_is_taken_as_it_was_put(self) -> None:
        mailbox = LiveMailbox()
        mailbox.put(b"one")
        assert mailbox.pending() is True
        assert await mailbox.take() == b"one"
        assert mailbox.pending() is False
        assert mailbox.delivered == 1
        assert mailbox.skipped == 0

    async def test_three_puts_then_one_take_give_the_last_frame(self) -> None:
        mailbox = LiveMailbox()
        mailbox.put(b"one")
        mailbox.put(b"two")
        mailbox.put(b"three")
        assert await mailbox.take() == b"three"
        assert mailbox.skipped == 2
        assert mailbox.delivered == 1
        assert mailbox.pending() is False

    async def test_fifty_puts_never_leave_more_than_one_frame(self) -> None:
        mailbox = LiveMailbox()
        for index in range(50):
            mailbox.put(str(index).encode())
        assert await mailbox.take() == b"49"
        assert mailbox.pending() is False
        assert mailbox.skipped == 49

    async def test_take_waits_for_a_frame(self) -> None:
        mailbox = LiveMailbox()
        taker = asyncio.create_task(mailbox.take())
        await asyncio.sleep(0.05)
        assert taker.done() is False
        mailbox.put(b"late")
        assert await asyncio.wait_for(taker, timeout=1.0) == b"late"

    async def test_take_on_an_empty_mailbox_times_out(self) -> None:
        with pytest.raises(asyncio.TimeoutError):
            await asyncio.wait_for(LiveMailbox().take(), timeout=0.05)

    async def test_a_frame_put_after_a_take_is_delivered_without_a_skip(self) -> None:
        mailbox = LiveMailbox()
        mailbox.put(b"one")
        await mailbox.take()
        mailbox.put(b"two")
        assert await mailbox.take() == b"two"
        assert mailbox.skipped == 0
        assert mailbox.delivered == 2
