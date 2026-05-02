#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: @spacemany2k38
# 2025-12-27

import base64
import sys
import time
import urllib.request
import urllib.error
import urllib.parse
from http.client import HTTPResponse

from app import __version__


USER_AGENT = f"purl/{__version__}"
MAX_REDIRECTS = 30


class Response:
    """Structured HTTP response."""

    __slots__ = (
        'status', 'reason', 'headers', 'body', 'url',
        'elapsed_ms', 'redirects', 'error',
    )

    def __init__(self):
        self.status = 0
        self.reason = ''
        self.headers = []
        self.body = b''
        self.url = ''
        self.elapsed_ms = 0.0
        self.redirects = []
        self.error = None

    @property
    def ok(self) -> bool:
        return 200 <= self.status < 400

    @property
    def is_json(self) -> bool:
        for key, val in self.headers:
            if key.lower() == 'content-type' and 'json' in val.lower():
                return True
        return False

    @property
    def content_type(self) -> str:
        for key, val in self.headers:
            if key.lower() == 'content-type':
                return val
        return ''

    @property
    def content_length(self) -> int:
        for key, val in self.headers:
            if key.lower() == 'content-length':
                try:
                    return int(val)
                except ValueError:
                    pass
        return -1


class HTTPFetcher:
    """HTTP client with redirect tracing, timing, and auth."""

    def __init__(
        self, timeout=30, follow_redirects=False,
        max_redirects=MAX_REDIRECTS, verify_ssl=True, verbose=False,
    ):
        self.timeout = timeout
        self.follow_redirects = follow_redirects
        self.max_redirects = max_redirects
        self.verify_ssl = verify_ssl
        self.verbose = verbose

    def fetch(
        self, url: str, method: str = 'GET', headers: dict = None,
        data: bytes = None, auth: tuple = None,
    ) -> Response:
        """Perform an HTTP request.

        Args:
            url: Target URL
            method: HTTP verb
            headers: Request headers dict
            data: Request body (bytes)
            auth: Tuple of (user, password) for Basic auth

        Returns:
            Response object with status, headers, body, timing, redirects.
        """
        resp = Response()
        resp.url = url
        headers = dict(headers) if headers else {}

        if 'User-Agent' not in headers:
            headers['User-Agent'] = USER_AGENT

        if auth:
            credentials = base64.b64encode(
                f"{auth[0]}:{auth[1]}".encode()
            ).decode()
            headers['Authorization'] = f'Basic {credentials}'

        ctx = None
        if not self.verify_ssl:
            import ssl
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE

        visited = set()
        current_url = url
        current_method = method
        current_data = data

        start = time.monotonic()

        for _ in range(self.max_redirects + 1):
            if current_url in visited:
                resp.error = 'Redirect loop detected'
                resp.elapsed_ms = (time.monotonic() - start) * 1000
                return resp
            visited.add(current_url)

            try:
                req = urllib.request.Request(current_url, method=current_method)
                for key, value in headers.items():
                    req.add_header(key, value)

                if current_data:
                    req.data = current_data

                opener = urllib.request.build_opener(
                    urllib.request.HTTPSHandler(context=ctx) if ctx else
                    urllib.request.HTTPSHandler(),
                    _NoRedirectHandler(),
                )

                raw = opener.open(req, timeout=self.timeout)

                resp.status = raw.status
                resp.reason = raw.reason
                resp.headers = list(raw.headers.items())
                resp.url = current_url
                resp.body = raw.read()
                break

            except urllib.error.HTTPError as e:
                status = e.code
                reason = e.reason
                hdrs = list(e.headers.items()) if e.headers else []
                try:
                    body = e.read()
                except Exception:
                    body = b''

                if self._is_redirect(status) and self.follow_redirects:
                    location = e.headers.get('Location', '') if e.headers else ''
                    if not location:
                        resp.status = status
                        resp.reason = reason
                        resp.headers = hdrs
                        resp.body = body
                        break

                    next_url = urllib.parse.urljoin(current_url, location)
                    resp.redirects.append((status, current_url, next_url))

                    if self.verbose:
                        print(
                            f"* Redirect {status} -> {next_url}",
                            file=sys.stderr,
                        )

                    current_url = next_url
                    if status in (301, 302, 303):
                        current_method = 'GET'
                        current_data = None
                    continue

                resp.status = status
                resp.reason = reason
                resp.headers = hdrs
                resp.body = body
                break

            except urllib.error.URLError as e:
                resp.error = str(e.reason)
                break

            except OSError as e:
                resp.error = str(e)
                break

            except Exception as e:
                resp.error = str(e)
                break

        resp.elapsed_ms = (time.monotonic() - start) * 1000
        return resp

    @staticmethod
    def _is_redirect(status: int) -> bool:
        return status in (301, 302, 303, 307, 308)


class _NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Prevent urllib from auto-following redirects so we control the flow."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None
