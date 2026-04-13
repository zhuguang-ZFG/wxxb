from __future__ import annotations

import asyncio
from typing import TextIO

from linktunnel.logfmt import log_line


async def create_tcp_proxy_server(
    listen_host: str,
    listen_port: int,
    target_host: str,
    target_port: int,
    *,
    log_stream: TextIO | None,
    hex_log: bool,
) -> asyncio.Server:
    async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        peer = writer.get_extra_info("peername")
        try:
            tr, tw = await asyncio.open_connection(target_host, target_port)
        except OSError as e:
            writer.close()
            await writer.wait_closed()
            if log_stream:
                log_stream.write(f"[tcp] client {peer} upstream connect failed: {e}\n")
                log_stream.flush()
            return

        async def pump(
            src: asyncio.StreamReader,
            dst: asyncio.StreamWriter,
            direction: str,
            *,
            eof_peer: asyncio.StreamWriter | None = None,
        ) -> None:
            try:
                while True:
                    data = await src.read(65536)
                    if not data:
                        break
                    if log_stream is not None:
                        log_line(log_stream, direction, data, hex_mode=hex_log)
                    dst.write(data)
                    await dst.drain()
            finally:
                if eof_peer is not None and not eof_peer.is_closing():
                    try:
                        eof_peer.write_eof()
                    except (AttributeError, OSError, RuntimeError):
                        pass

        try:
            await asyncio.gather(
                pump(reader, tw, "tcp client->upstream", eof_peer=tw),
                pump(tr, writer, "tcp upstream->client", eof_peer=writer),
            )
        finally:
            for w in (writer, tw):
                try:
                    if not w.is_closing():
                        w.close()
                    await w.wait_closed()
                except Exception:
                    pass

    server = await asyncio.start_server(handle_client, listen_host, listen_port)
    if log_stream is not None and server.sockets:
        addrs = ", ".join(str(sock.getsockname()) for sock in server.sockets)
        log_stream.write(f"[tcp] listening {addrs} -> {target_host}:{target_port}\n")
        log_stream.flush()
    return server


async def tcp_proxy(
    listen_host: str,
    listen_port: int,
    target_host: str,
    target_port: int,
    *,
    log_stream: TextIO | None,
    hex_log: bool,
) -> None:
    server = await create_tcp_proxy_server(
        listen_host,
        listen_port,
        target_host,
        target_port,
        log_stream=log_stream,
        hex_log=hex_log,
    )
    async with server:
        await server.serve_forever()


def run_tcp_proxy(
    listen_host: str,
    listen_port: int,
    target_host: str,
    target_port: int,
    *,
    log_stream: TextIO | None,
    hex_log: bool,
) -> None:
    asyncio.run(
        tcp_proxy(
            listen_host,
            listen_port,
            target_host,
            target_port,
            log_stream=log_stream,
            hex_log=hex_log,
        )
    )


async def udp_relay(
    listen_host: str,
    listen_port: int,
    target_host: str,
    target_port: int,
    *,
    log_stream: TextIO | None,
    hex_log: bool,
) -> None:
    loop = asyncio.get_running_loop()
    last_client: list[tuple[str, int] | None] = [None]
    local_t: list[asyncio.DatagramTransport | None] = [None]
    remote_t: list[asyncio.DatagramTransport | None] = [None]
    target = (target_host, target_port)

    class RemoteProto(asyncio.DatagramProtocol):
        def datagram_received(self, data: bytes, _addr: tuple[str | int | None, int]) -> None:
            c = last_client[0]
            lt = local_t[0]
            if c and lt is not None:
                if log_stream is not None:
                    log_line(
                        log_stream,
                        f"udp upstream->{c[0]}:{c[1]}",
                        data,
                        hex_mode=hex_log,
                    )
                lt.sendto(data, c)

    class LocalProto(asyncio.DatagramProtocol):
        def datagram_received(self, data: bytes, addr: tuple[str | int | None, int]) -> None:
            a = (str(addr[0] or "0.0.0.0"), int(addr[1]))
            last_client[0] = a
            rt = remote_t[0]
            if rt is not None:
                if log_stream is not None:
                    log_line(
                        log_stream,
                        f"udp {a[0]}:{a[1]}->{target_host}:{target_port}",
                        data,
                        hex_mode=hex_log,
                    )
                rt.sendto(data, target)

    _r, _ = await loop.create_datagram_endpoint(RemoteProto, local_addr=("0.0.0.0", 0))
    remote_t[0] = _r
    _l, _ = await loop.create_datagram_endpoint(LocalProto, local_addr=(listen_host, listen_port))
    local_t[0] = _l
    if log_stream is not None:
        la = _l.get_extra_info("sockname")
        ra = _r.get_extra_info("sockname")
        log_stream.write(
            f"[udp] relay {la} <-> upstream {target_host}:{target_port} (via local {ra})\n"
        )
        log_stream.flush()

    await asyncio.Future()


def run_udp_relay(
    listen_host: str,
    listen_port: int,
    target_host: str,
    target_port: int,
    *,
    log_stream: TextIO | None,
    hex_log: bool,
) -> None:
    asyncio.run(
        udp_relay(
            listen_host,
            listen_port,
            target_host,
            target_port,
            log_stream=log_stream,
            hex_log=hex_log,
        )
    )
