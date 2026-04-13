from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass
class StatusReport:
    raw: str
    state: str
    fields: dict[str, str] = field(default_factory=dict)

    def format_human(self) -> str:
        lines = [f"state: {self.state}"]
        for k, v in sorted(self.fields.items()):
            lines.append(f"  {k}: {v}")
        return "\n".join(lines)


_STATUS_RE = re.compile(r"^<(.+)>$")


def parse_status_report(line: str) -> StatusReport | None:
    """Parse a Grbl 1.1 style status line ``<Idle|MPos:...>``."""
    s = line.strip()
    m = _STATUS_RE.match(s)
    if not m:
        return None
    inner = m.group(1)
    parts = inner.split("|")
    if not parts:
        return StatusReport(raw=s, state="?")
    state = parts[0].strip()
    fields: dict[str, str] = {}
    for p in parts[1:]:
        p = p.strip()
        if not p:
            continue
        if ":" in p:
            k, v = p.split(":", 1)
            fields[k.strip()] = v.strip()
        else:
            fields[p] = ""
    return StatusReport(raw=s, state=state, fields=fields)
