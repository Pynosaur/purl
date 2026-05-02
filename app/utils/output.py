#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: @spacemany2k38
# 2025-12-27

import sys
from pathlib import Path


def write_to_file(content: bytes, filepath: str, verbose: bool = False) -> bool:
    """Write content to file.

    Returns True on success, False on error.
    """
    try:
        Path(filepath).write_bytes(content)
        if verbose:
            print(f"* Saved to {filepath}", file=sys.stderr)
        return True
    except OSError as e:
        print(f"purl: cannot write {filepath}: {e}", file=sys.stderr)
        return False


def write_to_stdout(content: bytes) -> bool:
    """Write content to stdout.

    Returns True on success, False on error.
    """
    try:
        try:
            print(content.decode('utf-8'), end='')
        except UnicodeDecodeError:
            sys.stdout.buffer.write(content)
        return True
    except OSError as e:
        print(f"purl: output error: {e}", file=sys.stderr)
        return False
