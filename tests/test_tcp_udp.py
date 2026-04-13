from __future__ import annotations

import asyncio
import contextlib
import socket
from io import StringIO

import pytest

from linktunnel.tcp_udp import create_tcp_proxy_server, udp_relay


@pytest.mark.asyncio
async def test_tcp_proxy_forwards_to_echo() -> None:
    async def echo(
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
    ) -> None:
        data = await reader.read(4096)
        if data:
            writer.write(data)
            await writer.drain()
        writer.close()
        await writer.wait_closed()

    echo_srv = await asyncio.start_server(echo, "127.0.0.1", 0)
    echo_port = echo_srv.sockets[0].getsockname()[1]

    log = StringIO()
    proxy_srv = await create_tcp_proxy_server(
        "127.0.0.1",
        0,
        "127.0.0.1",
        echo_port,
        log_stream=log,
        hex_log=False,
    )
    proxy_port = proxy_srv.sockets[0].getsockname()[1]

    async with echo_srv:
        async with proxy_srv:
            await echo_srv.start_serving()
            await proxy_srv.start_serving()
            reader, writer = await asyncio.open_connection("127.0.0.1", proxy_port)
            writer.write(b"ping")
            await writer.drain()
            got = await asyncio.wait_for(reader.read(16), timeout=3)
            writer.close()
            await writer.wait_closed()
            assert got == b"ping"

    assert "[tcp] listening" in log.getvalue()


def _udp_free_port() -> int:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


@pytest.mark.asyncio
async def test_udp_relay_roundtrip() -> None:
    loop = asyncio.get_running_loop()

    class EchoProto(asyncio.DatagramProtocol):
        def connection_made(self, transport: asyncio.DatagramTransport) -> None:
            self.transport = transport

        def datagram_received(self, data: bytes, addr: tuple[object, ...]) -> None:
            self.transport.sendto(data, addr)

    echo_port = _udp_free_port()
    listen_port = _udp_free_port()

    echo_t, _echo_p = await loop.create_datagram_endpoint(
        EchoProto,
        local_addr=("127.0.0.1", echo_port),
    )

    relay_task = asyncio.create_task(
        udp_relay(
            "127.0.0.1",
            listen_port,
            "127.0.0.1",
            echo_port,
            log_stream=None,
            hex_log=False,
        )
    )
    await asyncio.sleep(0.05)

    class ClientProto(asyncio.DatagramProtocol):
        def __init__(self) -> None:
            self.fut: asyncio.Future[bytes] = loop.create_future()
            self.transport: asyncio.DatagramTransport | None = None

        def connection_made(self, transport: asyncio.DatagramTransport) -> None:
            self.transport = transport

        def datagram_received(self, data: bytes, _addr: object) -> None:
            if not self.fut.done():
                self.fut.set_result(data)

    client_t, proto = await loop.create_datagram_endpoint(
        ClientProto,
        local_addr=("127.0.0.1", 0),
    )
    assert proto.transport is not None
    proto.transport.sendto(b"ping", ("127.0.0.1", listen_port))
    try:
        data = await asyncio.wait_for(proto.fut, timeout=3)
    finally:
        relay_task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await relay_task
        client_t.close()
        echo_t.close()

    assert data == b"ping"
