from __future__ import annotations

# Standard library imports
import asyncio
from asyncio import StreamReader, StreamWriter
from typing import ClassVar, Optional, Set, Tuple


class LinkProxy:
    """A real TCP proxy standing in for the network link between an edge and a core."""

    HOST: ClassVar[str] = "127.0.0.1"
    CHUNK_BYTES: ClassVar[int] = 65536

    def __init__(self, target_port: int) -> None:
        self.target_port = target_port
        self.cut_now = False
        self.server: Optional[asyncio.AbstractServer] = None
        self.pairs: Set[Tuple[StreamWriter, StreamWriter]] = set()
        self.tasks: Set[asyncio.Future[None]] = set()

    ############################
    # Internal Helpers Methods #
    ############################

    async def _pipe(self, reader: StreamReader, writer: StreamWriter) -> None:
        try:
            while True:
                chunk = await reader.read(self.CHUNK_BYTES)
                if not chunk:
                    break
                writer.write(chunk)
                await writer.drain()
        except (ConnectionError, OSError):
            pass
        finally:
            writer.close()

    async def _close_pair(self, pair: Tuple[StreamWriter, StreamWriter]) -> None:
        for writer in pair:
            try:
                writer.close()
                await writer.wait_closed()
            except (ConnectionError, OSError):
                pass

    async def _accept(self, reader: StreamReader, writer: StreamWriter) -> None:
        if self.cut_now:
            await self._close_pair((writer, writer))
            return
        try:
            target_reader, target_writer = await asyncio.open_connection(self.HOST, self.target_port)
        except OSError:
            await self._close_pair((writer, writer))
            return
        pair = (writer, target_writer)
        self.pairs.add(pair)
        forward = asyncio.ensure_future(self._pipe(reader, target_writer))
        backward = asyncio.ensure_future(self._pipe(target_reader, writer))
        self.tasks.update({forward, backward})
        try:
            await asyncio.gather(forward, backward)
        except (ConnectionError, OSError):
            pass
        finally:
            self.pairs.discard(pair)
            self.tasks.discard(forward)
            self.tasks.discard(backward)

    ############################
    # Publicly Exposed Methods #
    ############################

    async def listen(self) -> int:
        self.server = await asyncio.start_server(self._accept, self.HOST, 0)
        return int(self.server.sockets[0].getsockname()[1])

    async def cut(self) -> None:
        self.cut_now = True
        for pair in list(self.pairs):
            await self._close_pair(pair)

    async def restore(self) -> None:
        self.cut_now = False

    async def close(self) -> None:
        """Close the proxied connections first: since Python 3.12, wait_closed waits for every open handler."""
        self.cut_now = True
        if self.server is not None:
            self.server.close()
        for pair in list(self.pairs):
            await self._close_pair(pair)
        for task in list(self.tasks):
            task.cancel()
        await asyncio.gather(*self.tasks, return_exceptions=True)
        self.pairs = set()
        self.tasks = set()
        if self.server is not None:
            await self.server.wait_closed()
