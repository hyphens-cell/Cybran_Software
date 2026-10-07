"""Helpers for advertising the local Waitress server to phones on the LAN."""
from __future__ import annotations

import ipaddress
import os
import socket
from collections.abc import Iterable


def _usable_ipv4(addresses: Iterable[str]) -> list[str]:
    result: list[str] = []
    for address in addresses:
        try:
            parsed = ipaddress.ip_address(address)
        except ValueError:
            continue
        if parsed.version != 4 or parsed.is_loopback or parsed.is_link_local or not parsed.is_private:
            continue
        if address not in result:
            result.append(address)
    return result


def discover_lan_ipv4() -> list[str]:
    """Return likely phone-reachable private addresses, primary route first."""
    candidates: list[str] = []
    # A UDP connect selects a route but sends no traffic.
    for destination in (("192.0.2.1", 80), ("8.8.8.8", 80)):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as probe:
                probe.connect(destination)
                candidates.append(probe.getsockname()[0])
            break
        except OSError:
            continue
    try:
        candidates.extend(item[4][0] for item in socket.getaddrinfo(
            socket.gethostname(), None, socket.AF_INET, socket.SOCK_STREAM
        ))
    except OSError:
        pass
    override = os.environ.get("MOBILE_IP", "").strip()
    if override:
        candidates.insert(0, override)
    return _usable_ipv4(candidates)


def mobile_urls(port: int) -> list[str]:
    if not 1 <= port <= 65535:
        raise ValueError("PORT must be between 1 and 65535")
    return [f"http://{address}:{port}" for address in discover_lan_ipv4()]


def render_terminal_qr(value: str) -> str:
    """Render a compact high-contrast QR suitable for Windows terminals."""
    import qrcode

    qr = qrcode.QRCode(version=None, error_correction=qrcode.constants.ERROR_CORRECT_M,
                       box_size=1, border=2)
    qr.add_data(value)
    qr.make(fit=True)
    matrix = qr.get_matrix()
    lines: list[str] = []
    for row_index in range(0, len(matrix), 2):
        top = matrix[row_index]
        bottom = matrix[row_index + 1] if row_index + 1 < len(matrix) else [False] * len(top)
        lines.append("".join("█" if upper and lower else "▀" if upper else "▄" if lower else " "
                             for upper, lower in zip(top, bottom)))
    return "\n".join(lines)
