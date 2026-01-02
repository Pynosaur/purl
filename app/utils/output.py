#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: @spacemany2k38
# 2025-12-27

import sys
from pathlib import Path


def write_to_file(content, filepath, verbose=False):
    """Write content to file.
    
    Args:
        content: Bytes to write
        filepath: Path to output file
        verbose: Print status message
    
    Returns:
        True if successful, False otherwise
    """
    try:
        output_path = Path(filepath)
        output_path.write_bytes(content)
        
        if verbose:
            print(f"Saved to {filepath}", file=sys.stderr)
        
        return True
    except Exception as e:
        print(f"purl: Failed to write {filepath}: {e}", file=sys.stderr)
        return False


def write_to_stdout(content):
    """Write content to stdout.
    
    Args:
        content: Bytes to write
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # Try to decode as text
        try:
            print(content.decode('utf-8'), end='')
        except UnicodeDecodeError:
            # Binary content - write to stdout buffer
            sys.stdout.buffer.write(content)
        
        return True
    except Exception as e:
        print(f"purl: Output error: {e}", file=sys.stderr)
        return False


def print_headers(header_lines):
    """Print headers to stderr.
    
    Args:
        header_lines: List of header strings
    """
    for line in header_lines:
        print(f"< {line}", file=sys.stderr)
    print("", file=sys.stderr)


def print_request_info(method, url, headers_dict):
    """Print request information for verbose mode.
    
    Args:
        method: HTTP method
        url: Request URL
        headers_dict: Dict of request headers
    """
    print(f"> {method} {url}", file=sys.stderr)
    for key, value in headers_dict.items():
        print(f"> {key}: {value}", file=sys.stderr)
    print("", file=sys.stderr)

