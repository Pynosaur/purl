#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import unittest
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.main import print_help, print_version
from app.core.fetcher import HTTPFetcher
from app.utils.headers import parse_header, parse_headers
from app.utils.output import write_to_file


class TestPurl(unittest.TestCase):
    """Test cases for purl command."""
    
    def test_help(self):
        """Test help function doesn't crash."""
        try:
            print_help()
        except Exception as e:
            self.fail(f"print_help raised {e}")
    
    def test_version(self):
        """Test version function doesn't crash."""
        try:
            print_version()
        except Exception as e:
            self.fail(f"print_version raised {e}")


class TestHeaders(unittest.TestCase):
    """Test header parsing."""
    
    def test_parse_header(self):
        """Test parsing single header."""
        result = parse_header("Content-Type: application/json")
        self.assertEqual(result, ("Content-Type", "application/json"))
    
    def test_parse_header_with_spaces(self):
        """Test parsing header with extra spaces."""
        result = parse_header("  Authorization:  Bearer token  ")
        self.assertEqual(result, ("Authorization", "Bearer token"))
    
    def test_parse_header_invalid(self):
        """Test parsing invalid header."""
        result = parse_header("InvalidHeader")
        self.assertIsNone(result)
    
    def test_parse_headers_list(self):
        """Test parsing list of headers."""
        headers = ["Accept: application/json", "User-Agent: purl/0.1.0"]
        result = parse_headers(headers)
        self.assertEqual(result['Accept'], 'application/json')
        self.assertEqual(result['User-Agent'], 'purl/0.1.0')


class TestFetcher(unittest.TestCase):
    """Test HTTP fetching (requires network)."""
    
    def test_fetch_url_basic(self):
        """Test basic URL fetching."""
        fetcher = HTTPFetcher()
        success, response, content = fetcher.fetch("https://httpbin.org/status/200")
        self.assertTrue(success, "Should successfully fetch URL")
        self.assertIsNotNone(content)
    
    def test_fetch_url_404(self):
        """Test handling 404 errors."""
        fetcher = HTTPFetcher()
        success, response, content = fetcher.fetch("https://httpbin.org/status/404")
        self.assertFalse(success, "Should return False for 404")
    
    def test_fetch_url_with_headers(self):
        """Test fetching with custom headers."""
        fetcher = HTTPFetcher()
        headers = {"Accept": "application/json"}
        success, response, content = fetcher.fetch("https://httpbin.org/get", headers=headers)
        self.assertTrue(success, "Should successfully fetch with headers")


if __name__ == "__main__":
    unittest.main()
