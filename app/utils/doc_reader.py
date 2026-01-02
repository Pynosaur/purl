#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: @spacemany2k38
# 2025-12-27

import re
import sys
from pathlib import Path


def read_app_doc(app_name):
    """Read app documentation from YAML file.
    
    Args:
        app_name: Name of the app (e.g., 'purl')
    
    Returns:
        Dict with version, description, usage, options, examples
    """
    doc_paths = [
        Path(__file__).parent.parent.parent.parent / "doc" / f"{app_name}.yaml",  # Source
        Path("doc") / f"{app_name}.yaml",  # Bundled
    ]
    
    # Nuitka onefile support
    if hasattr(sys, '_MEIPASS'):
        doc_paths.insert(0, Path(sys._MEIPASS) / "doc" / f"{app_name}.yaml")
    
    for path in doc_paths:
        if path.exists():
            try:
                content = path.read_text()
                
                # Extract VERSION
                version = re.search(r'^VERSION:\s*"([^"]+)"', content, re.MULTILINE)
                version = version.group(1) if version else ''
                
                # Extract DESCRIPTION
                desc = re.search(r'^DESCRIPTION:\s*>\s*(.+?)(?=^[A-Z_]+:)', content, re.MULTILINE | re.DOTALL)
                desc = desc.group(1).strip() if desc else ''
                
                # Extract USAGE items
                usage_section = re.search(r'^USAGE:(.+?)^OPTIONS:', content, re.MULTILINE | re.DOTALL)
                usage = re.findall(r'-\s*"([^"]+)"', usage_section.group(1)) if usage_section else []
                
                # Extract OPTIONS items
                options_section = re.search(r'^OPTIONS:(.+?)^EXAMPLES:', content, re.MULTILINE | re.DOTALL)
                options = re.findall(r'-\s*"([^"]+)"', options_section.group(1)) if options_section else []
                
                # Extract EXAMPLES items
                examples_section = re.search(r'^EXAMPLES:(.+?)^OUTPUT:', content, re.MULTILINE | re.DOTALL)
                examples = re.findall(r'-\s*"([^"]+)"', examples_section.group(1)) if examples_section else []
                
                return {
                    'version': version,
                    'description': desc,
                    'usage': usage,
                    'options': options,
                    'examples': examples
                }
            except (OSError, UnicodeDecodeError):
                continue
    
    return {}

