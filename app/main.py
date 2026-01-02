#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: @spacemany2k38
# 2025-12-27

import argparse
import sys
from pathlib import Path

# Allow running both as module and as script
if __name__ == "__main__" and __package__ is None:
    sys.path.append(str(Path(__file__).resolve().parent.parent))
    __package__ = "app"

from app import __version__
from app.core.fetcher import HTTPFetcher
from app.utils.headers import parse_headers, format_response_headers
from app.utils.output import write_to_file, write_to_stdout, print_headers, print_request_info
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


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Transfer data from URLs',
        add_help=False
    )
    
    parser.add_argument('url', nargs='?', help='URL to fetch')
    parser.add_argument('-h', '--help', action='store_true', help='Show help')
    parser.add_argument('-v', '--version', action='store_true', help='Show version')
    parser.add_argument('-o', '--output', metavar='FILE', help='Write output to file')
    parser.add_argument('-H', '--header', action='append', metavar='HEADER', help='Add header')
    parser.add_argument('-X', '--request', metavar='METHOD', default='GET', help='HTTP method')
    parser.add_argument('-d', '--data', metavar='DATA', help='HTTP POST data')
    parser.add_argument('-i', '--include', action='store_true', help='Include response headers')
    parser.add_argument('-L', '--location', action='store_true', help='Follow redirects')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    if args.help:
        print_help()
        return 0
    
    if args.version:
        print_version()
        return 0
    
    if not args.url:
        print("purl: URL required", file=sys.stderr)
        print("Try 'purl --help' for more information", file=sys.stderr)
        return 1
    
    # Parse headers
    headers_dict = parse_headers(args.header)
    
    # Create fetcher
    fetcher = HTTPFetcher(verbose=args.verbose)
    
    # Print request info if verbose
    if args.verbose:
        print_request_info(args.request, args.url, headers_dict)
    
    # Fetch URL
    success, response, content = fetcher.fetch(
        url=args.url,
        method=args.request,
        headers=headers_dict,
        data=args.data
    )
    
    if not success:
        return 1
    
    # Display response headers if requested
    if args.include or args.verbose:
        header_lines = format_response_headers(response)
        print_headers(header_lines)
    
    # Write output
    if args.output:
        success = write_to_file(content, args.output, verbose=args.verbose)
    else:
        success = write_to_stdout(content)
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
