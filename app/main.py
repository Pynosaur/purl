#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: @spacemany2k38
# 2025-12-27

import sys
from pathlib import Path

if __name__ == "__main__" and __package__ is None:
    sys.path.append(str(Path(__file__).resolve().parent.parent))
    __package__ = "app"

from app import __version__
from app.core.fetcher import HTTPFetcher, Response
from app.core.formatter import (
    supports_color,
    format_status_line,
    format_response_headers,
    format_request_line,
    format_request_headers,
    format_timing,
    format_redirect_chain,
    format_size,
    format_json,
)
from app.utils.headers import parse_headers
from app.utils.doc_reader import read_app_doc


def print_help():
    """Print help message from documentation."""
    doc = read_app_doc('purl')

    desc = doc.get('description', 'Transfer data from URLs')
    usage = doc.get('usage', ['purl [OPTIONS] URL'])
    options = doc.get('options', [])
    examples = doc.get('examples', [])

    print(f"purl - {desc}")
    print("\nUSAGE:")
    for u in usage:
        print(f"    {u}")

    if options:
        print("\nOPTIONS:")
        for opt in options:
            print(f"    {opt}")

    if examples:
        print("\nEXAMPLES:")
        for ex in examples:
            print(f"    {ex}")


def print_version():
    """Print version from documentation."""
    doc = read_app_doc('purl')
    print(doc.get('version', __version__))


def read_body(data_arg: str) -> bytes:
    """Read request body from argument, file, or stdin.

    Supports:
        -d 'raw data'      -> literal body
        -d @filename       -> read from file
        -d @-              -> read from stdin
    """
    if data_arg == '@-':
        return sys.stdin.buffer.read()

    if data_arg.startswith('@'):
        filepath = Path(data_arg[1:])
        if not filepath.exists():
            print(f"purl: cannot read {filepath}: No such file", file=sys.stderr)
            sys.exit(1)
        return filepath.read_bytes()

    return data_arg.encode('utf-8')


def parse_auth(auth_str: str):
    """Parse user:password string."""
    if ':' not in auth_str:
        return (auth_str, '')
    user, password = auth_str.split(':', 1)
    return (user, password)


def main():
    """Main entry point."""
    args = sys.argv[1:]

    if not args or args[0] in ('-h', '--help', 'help'):
        print_help()
        return 0

    if args[0] in ('-v', '--version'):
        print_version()
        return 0

    url = None
    method = None
    header_list = []
    data_arg = None
    output_file = None
    include_headers = False
    follow_redirects = False
    verbose = False
    timeout = 30
    fail_on_error = False
    json_pretty = False
    auth_str = None
    no_color = False
    verify_ssl = True

    i = 0
    while i < len(args):
        arg = args[i]

        if arg in ('-X', '--request') and i + 1 < len(args):
            method = args[i + 1].upper()
            i += 2
        elif arg in ('-H', '--header') and i + 1 < len(args):
            header_list.append(args[i + 1])
            i += 2
        elif arg in ('-d', '--data') and i + 1 < len(args):
            data_arg = args[i + 1]
            i += 2
        elif arg in ('-o', '--output') and i + 1 < len(args):
            output_file = args[i + 1]
            i += 2
        elif arg in ('-u', '--user') and i + 1 < len(args):
            auth_str = args[i + 1]
            i += 2
        elif arg in ('--timeout',) and i + 1 < len(args):
            try:
                timeout = float(args[i + 1])
                if timeout <= 0:
                    print("purl: timeout must be > 0", file=sys.stderr)
                    return 1
            except ValueError:
                print(f"purl: invalid timeout: {args[i + 1]}", file=sys.stderr)
                return 1
            i += 2
        elif arg in ('-i', '--include'):
            include_headers = True
            i += 1
        elif arg in ('-L', '--location'):
            follow_redirects = True
            i += 1
        elif arg in ('-f', '--fail'):
            fail_on_error = True
            i += 1
        elif arg in ('-j', '--json'):
            json_pretty = True
            i += 1
        elif arg == '--no-color':
            no_color = True
            i += 1
        elif arg == '--no-verify-ssl':
            verify_ssl = False
            i += 1
        elif arg == '--verbose':
            verbose = True
            i += 1
        elif arg.startswith('-') and len(arg) > 1 and not arg.startswith('http'):
            print(f"purl: unknown option: {arg}", file=sys.stderr)
            print("Try 'purl --help' for more information", file=sys.stderr)
            return 1
        else:
            url = arg
            i += 1

    if not url:
        print("purl: URL required", file=sys.stderr)
        print("Try 'purl --help' for more information", file=sys.stderr)
        return 1

    if not url.startswith(('http://', 'https://')):
        url = f'https://{url}'

    # -d implies POST unless method explicitly set
    if data_arg and not method:
        method = 'POST'
    if not method:
        method = 'GET'

    headers_dict = parse_headers(header_list)
    color = supports_color() and not no_color
    auth = parse_auth(auth_str) if auth_str else None

    body = read_body(data_arg) if data_arg else None

    # Verbose: show request
    if verbose:
        print(format_request_line(method, url, color), file=sys.stderr)
        for line in format_request_headers(headers_dict, color):
            print(line, file=sys.stderr)
        if body:
            print(f"> Content-Length: {len(body)}", file=sys.stderr)
        print(file=sys.stderr)

    fetcher = HTTPFetcher(
        timeout=timeout,
        follow_redirects=follow_redirects,
        verify_ssl=verify_ssl,
        verbose=verbose,
    )

    resp = fetcher.fetch(
        url=url,
        method=method,
        headers=headers_dict,
        data=body,
        auth=auth,
    )

    if resp.error:
        print(f"purl: {resp.error}", file=sys.stderr)
        return 1

    # Show redirect chain in verbose mode
    if verbose and resp.redirects:
        for line in format_redirect_chain(resp.redirects, color):
            print(line, file=sys.stderr)
        print(file=sys.stderr)

    # Show response headers
    if include_headers or verbose:
        status_line = format_status_line(resp.status, resp.reason, color)
        print(f"< {status_line}", file=sys.stderr)
        for line in format_response_headers(resp.headers, color):
            print(f"< {line}", file=sys.stderr)
        print(file=sys.stderr)

    # Show timing in verbose mode
    if verbose:
        timing = format_timing(resp.elapsed_ms, color)
        size = format_size(len(resp.body))
        print(f"* Time: {timing} | Size: {size}", file=sys.stderr)
        print(file=sys.stderr)

    # Write output
    if output_file:
        try:
            Path(output_file).write_bytes(resp.body)
            if verbose:
                print(f"* Saved to {output_file}", file=sys.stderr)
        except OSError as e:
            print(f"purl: cannot write {output_file}: {e}", file=sys.stderr)
            return 1
    else:
        if json_pretty or (verbose and resp.is_json):
            text = format_json(resp.body)
            print(text)
        else:
            try:
                print(resp.body.decode('utf-8'), end='')
            except UnicodeDecodeError:
                sys.stdout.buffer.write(resp.body)

    # Exit code
    if fail_on_error and resp.status >= 400:
        return 22
    return 0


if __name__ == "__main__":
    sys.exit(main())
