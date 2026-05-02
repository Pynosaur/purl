#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: @spacemany2k38

import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.main import print_help, print_version, read_body, parse_auth
from app.core.fetcher import HTTPFetcher, Response
from app.core.formatter import (
    status_color,
    format_status_line,
    format_timing,
    format_size,
    format_json,
)
from app.utils.headers import parse_header, parse_headers


class TestHelp(unittest.TestCase):
    """Help and version don't crash."""

    def test_help(self):
        try:
            print_help()
        except Exception as e:
            self.fail(f"print_help raised {e}")

    def test_version(self):
        try:
            print_version()
        except Exception as e:
            self.fail(f"print_version raised {e}")


class TestHeaders(unittest.TestCase):
    """Header parsing."""

    def test_parse_single(self):
        self.assertEqual(
            parse_header("Content-Type: application/json"),
            ("Content-Type", "application/json"),
        )

    def test_parse_with_spaces(self):
        self.assertEqual(
            parse_header(" Authorization : Bearer token "),
            ("Authorization", "Bearer token"),
        )

    def test_parse_invalid(self):
        self.assertIsNone(parse_header("NoColonHere"))

    def test_parse_list(self):
        headers = ["Accept: text/html", "X-Custom: value"]
        result = parse_headers(headers)
        self.assertEqual(result['Accept'], 'text/html')
        self.assertEqual(result['X-Custom'], 'value')

    def test_parse_empty(self):
        self.assertEqual(parse_headers(None), {})
        self.assertEqual(parse_headers([]), {})


class TestReadBody(unittest.TestCase):
    """Body reading from string, file, stdin."""

    def test_literal_string(self):
        self.assertEqual(read_body('hello'), b'hello')

    def test_from_file(self, tmp_path=None):
        tmp = Path('/tmp/purl_test_body.txt')
        tmp.write_text('file content')
        try:
            self.assertEqual(read_body('@/tmp/purl_test_body.txt'), b'file content')
        finally:
            tmp.unlink(missing_ok=True)

    def test_json_body(self):
        body = read_body('{"key": "value"}')
        self.assertEqual(body, b'{"key": "value"}')


class TestParseAuth(unittest.TestCase):
    """Auth string parsing."""

    def test_user_pass(self):
        self.assertEqual(parse_auth('admin:secret'), ('admin', 'secret'))

    def test_user_only(self):
        self.assertEqual(parse_auth('admin'), ('admin', ''))

    def test_pass_with_colon(self):
        self.assertEqual(parse_auth('user:pass:word'), ('user', 'pass:word'))


class TestFormatter(unittest.TestCase):
    """Formatter utilities."""

    def test_format_size_bytes(self):
        self.assertEqual(format_size(500), '500B')

    def test_format_size_kb(self):
        self.assertEqual(format_size(2048), '2.0KB')

    def test_format_size_mb(self):
        self.assertEqual(format_size(2 * 1024 * 1024), '2.0MB')

    def test_format_size_unknown(self):
        self.assertEqual(format_size(-1), '?')

    def test_format_json_valid(self):
        result = format_json(b'{"a":1,"b":2}')
        self.assertIn('"a": 1', result)
        self.assertIn('"b": 2', result)

    def test_format_json_invalid(self):
        result = format_json(b'not json')
        self.assertEqual(result, 'not json')

    def test_status_color_no_color(self):
        self.assertEqual(status_color(200, False), '200')
        self.assertEqual(status_color(404, False), '404')


class TestFetcher(unittest.TestCase):
    """HTTP fetching (requires network)."""

    def test_get_200(self):
        fetcher = HTTPFetcher(timeout=10)
        resp = fetcher.fetch("https://httpbin.org/status/200")
        self.assertIsNone(resp.error)
        self.assertEqual(resp.status, 200)

    def test_get_404(self):
        fetcher = HTTPFetcher(timeout=10)
        resp = fetcher.fetch("https://httpbin.org/status/404")
        self.assertEqual(resp.status, 404)

    def test_post_data(self):
        fetcher = HTTPFetcher(timeout=10)
        resp = fetcher.fetch(
            "https://httpbin.org/post",
            method='POST',
            data=b'test=1',
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
        )
        self.assertIsNone(resp.error)
        self.assertEqual(resp.status, 200)

    def test_follow_redirects(self):
        fetcher = HTTPFetcher(timeout=10, follow_redirects=True)
        resp = fetcher.fetch("https://httpbin.org/redirect/2")
        self.assertEqual(resp.status, 200)
        self.assertEqual(len(resp.redirects), 2)

    def test_no_follow_redirects(self):
        fetcher = HTTPFetcher(timeout=10, follow_redirects=False)
        resp = fetcher.fetch("https://httpbin.org/redirect/1")
        self.assertEqual(resp.status, 302)
        self.assertEqual(len(resp.redirects), 0)

    def test_basic_auth(self):
        fetcher = HTTPFetcher(timeout=10)
        resp = fetcher.fetch(
            "https://httpbin.org/basic-auth/user/pass",
            auth=('user', 'pass'),
        )
        self.assertEqual(resp.status, 200)

    def test_timing(self):
        fetcher = HTTPFetcher(timeout=10)
        resp = fetcher.fetch("https://httpbin.org/get")
        self.assertGreater(resp.elapsed_ms, 0)

    def test_json_detection(self):
        fetcher = HTTPFetcher(timeout=10)
        resp = fetcher.fetch("https://httpbin.org/get")
        self.assertTrue(resp.is_json)


class TestResponse(unittest.TestCase):
    """Response object behavior."""

    def test_ok_property(self):
        r = Response()
        r.status = 200
        self.assertTrue(r.ok)
        r.status = 404
        self.assertFalse(r.ok)

    def test_is_json(self):
        r = Response()
        r.headers = [('Content-Type', 'application/json; charset=utf-8')]
        self.assertTrue(r.is_json)

    def test_content_length(self):
        r = Response()
        r.headers = [('Content-Length', '1234')]
        self.assertEqual(r.content_length, 1234)


if __name__ == "__main__":
    unittest.main()
