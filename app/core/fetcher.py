#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: @spacemany2k38
# 2025-12-27

import sys
import urllib.request
import urllib.error


class HTTPFetcher:
    """Handles HTTP requests."""
    
    def __init__(self, verbose=False):
        """Initialize fetcher.
        
        Args:
            verbose: Enable verbose output
        """
        self.verbose = verbose
    
    def fetch(self, url, method='GET', headers=None, data=None, timeout=30):
        """Fetch content from URL.
        
        Args:
            url: URL to fetch
            method: HTTP method (GET, POST, PUT, DELETE)
            headers: Dict of headers
            data: Data to send (str or bytes)
            timeout: Request timeout in seconds
        
        Returns:
            Tuple of (success, response_object, content_bytes)
        """
        try:
            # Build request
            req = urllib.request.Request(url, method=method)
            
            # Add headers
            if headers:
                for key, value in headers.items():
                    req.add_header(key, value)
            
            # Add data for POST/PUT
            if data:
                if isinstance(data, str):
                    data = data.encode('utf-8')
                req.data = data
            
            # Make request
            response = urllib.request.urlopen(req, timeout=timeout)
            content = response.read()
            
            return (True, response, content)
        
        except urllib.error.HTTPError as e:
            error_msg = f"HTTP error {e.code}: {e.reason}"
            print(f"purl: {error_msg}", file=sys.stderr)
            return (False, None, None)
        
        except urllib.error.URLError as e:
            print(f"purl: {e.reason}", file=sys.stderr)
            return (False, None, None)
        
        except Exception as e:
            print(f"purl: {e}", file=sys.stderr)
            return (False, None, None)

