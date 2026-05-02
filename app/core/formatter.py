#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: @spacemany2k38
# 2025-12-27

import json
import sys


GREEN = '\033[32m'
YELLOW = '\033[33m'
RED = '\033[31m'
CYAN = '\033[36m'
MAGENTA = '\033[35m'
BOLD = '\033[1m'
DIM = '\033[2m'
RESET = '\033[0m'


def supports_color() -> bool:
    if not hasattr(sys.stdout, 'isatty') or not sys.stdout.isatty():
        return False
    return True


def _c(text: str, code: str, enabled: bool) -> str:
    if not enabled:
        return text
    return f"{code}{text}{RESET}"


def status_color(status: int, color: bool) -> str:
    """Color-code HTTP status."""
    text = str(status)
    if not color:
        return text
    if status < 200:
        return f"{CYAN}{text}{RESET}"
    if status < 300:
        return f"{GREEN}{text}{RESET}"
    if status < 400:
        return f"{CYAN}{text}{RESET}"
    if status < 500:
        return f"{YELLOW}{text}{RESET}"
    return f"{RED}{text}{RESET}"


def format_status_line(status: int, reason: str, color: bool) -> str:
    """Format the HTTP status line."""
    code = status_color(status, color)
    return f"HTTP {code} {reason}"


def format_response_headers(headers: list, color: bool) -> list:
    """Format response headers with coloring."""
    lines = []
    for key, val in headers:
        k = _c(key, CYAN, color)
        lines.append(f"{k}: {val}")
    return lines


def format_request_line(method: str, url: str, color: bool) -> str:
    """Format request method and URL."""
    m = _c(method, BOLD, color)
    u = _c(url, DIM, color)
    return f"> {m} {u}"


def format_request_headers(headers: dict, color: bool) -> list:
    """Format request headers for verbose display."""
    lines = []
    for key, val in headers.items():
        k = _c(key, CYAN, color)
        lines.append(f"> {k}: {val}")
    return lines


def format_timing(elapsed_ms: float, color: bool) -> str:
    """Format response time."""
    if elapsed_ms < 100:
        c = GREEN
    elif elapsed_ms < 500:
        c = YELLOW
    else:
        c = RED

    if elapsed_ms >= 1000:
        text = f"{elapsed_ms / 1000:.2f}s"
    else:
        text = f"{elapsed_ms:.0f}ms"

    return _c(text, c, color)


def format_redirect_chain(redirects: list, color: bool) -> list:
    """Format redirect history."""
    lines = []
    for status, from_url, to_url in redirects:
        code = status_color(status, color)
        lines.append(f"* {code} {from_url} -> {_c(to_url, CYAN, color)}")
    return lines


def format_size(nbytes: int) -> str:
    """Human-readable byte size."""
    if nbytes < 0:
        return '?'
    if nbytes < 1024:
        return f"{nbytes}B"
    if nbytes < 1024 * 1024:
        return f"{nbytes / 1024:.1f}KB"
    return f"{nbytes / (1024 * 1024):.1f}MB"


def format_json(data: bytes) -> str:
    """Pretty-print JSON content. Returns original string on failure."""
    try:
        text = data.decode('utf-8')
        parsed = json.loads(text)
        return json.dumps(parsed, indent=2, ensure_ascii=False)
    except (ValueError, UnicodeDecodeError):
        return data.decode('utf-8', errors='replace')


def format_summary(status: int, elapsed_ms: float, size: int, color: bool) -> str:
    """One-line response summary for verbose mode."""
    parts = [
        format_status_line(status, '', color).rstrip(),
        format_timing(elapsed_ms, color),
        format_size(size),
    ]
    return ' | '.join(parts)
