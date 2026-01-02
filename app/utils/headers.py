#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: @spacemany2k38
# 2025-12-27


def parse_header(header_str):
    """Parse header string into key-value pair.
    
    Args:
        header_str: Header string like "Content-Type: application/json"
    
    Returns:
        Tuple of (key, value) or None if invalid
    """
    if ':' not in header_str:
        return None
    
    key, value = header_str.split(':', 1)
    return (key.strip(), value.strip())


def parse_headers(header_list):
    """Parse list of header strings.
    
    Args:
        header_list: List of header strings
    
    Returns:
        Dict of headers
    """
    if not header_list:
        return {}
    
    headers = {}
    for header_str in header_list:
        result = parse_header(header_str)
        if result:
            key, value = result
            headers[key] = value
    
    return headers


def format_response_headers(response):
    """Format response headers for display.
    
    Args:
        response: urllib response object
    
    Returns:
        List of formatted header lines
    """
    lines = []
    lines.append(f"Status: {response.status} {response.reason}")
    
    for key, value in response.headers.items():
        lines.append(f"{key}: {value}")
    
    return lines

