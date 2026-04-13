from __future__ import annotations


def parse_host_port(s: str) -> tuple[str, int]:
    """Parse host:port or [ipv6]:port. Empty host before last colon becomes 0.0.0.0."""
    s = s.strip()
    if not s:
        raise ValueError("empty address")
    if s.startswith("["):
        if "]" not in s:
            raise ValueError("invalid IPv6: missing ']'")
        end = s.index("]")
        host = s[1:end]
        rest = s[end + 1 :]
        if not rest.startswith(":"):
            raise ValueError("IPv6 must use form [addr]:port")
        port_s = rest[1:]
        if not port_s.isdigit():
            raise ValueError("port must be an integer")
        port = int(port_s)
        if not (0 < port < 65536):
            raise ValueError("port out of range")
        return host, port
    host, sep, port_s = s.rpartition(":")
    if not sep:
        raise ValueError("expected host:port or [ipv6]:port")
    if not port_s or not port_s.isdigit():
        raise ValueError("port must be an integer")
    port = int(port_s)
    if not (0 < port < 65536):
        raise ValueError("port out of range")
    if not host:
        host = "0.0.0.0"
    return host, port
