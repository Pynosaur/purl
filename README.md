# purl

Pure Python URL transfer tool (alternative to curl).

Version: 0.1.0

## Features

- HTTP GET, POST, PUT, DELETE requests
- Custom headers
- Download to file or stdout
- Follow redirects
- Response headers display
- Verbose mode
- Pure Python (no external dependencies)

## Usage

```bash
# Basic GET request
purl https://example.com

# Download to file
purl -o page.html https://example.com

# Show response headers
purl -i https://api.github.com

# Custom headers
purl -H "Accept: application/json" https://api.github.com

# POST request with data
purl -X POST -d "key=value" https://api.example.com

# Multiple headers
purl -H "Authorization: Bearer token" -H "Content-Type: application/json" https://api.example.com

# Verbose mode
purl --verbose https://example.com
```

## Options

- `-h, --help` - Show help message
- `-v, --version` - Show version information
- `-o, --output FILE` - Write output to file instead of stdout
- `-H, --header HEADER` - Add custom header (can be used multiple times)
- `-X, --request METHOD` - HTTP method (GET, POST, PUT, DELETE)
- `-d, --data DATA` - HTTP POST data
- `-i, --include` - Include response headers in output
- `-L, --location` - Follow redirects (default behavior)
- `--verbose` - Show verbose output

## Examples

Fetch a webpage:
```bash
purl https://example.com
```

Download a file:
```bash
purl -o archive.tar.gz https://example.com/file.tar.gz
```

API request with JSON:
```bash
purl -H "Accept: application/json" https://api.github.com/users/pynosaur
```

POST request:
```bash
purl -X POST -d '{"key":"value"}' -H "Content-Type: application/json" https://api.example.com
```

Check headers:
```bash
purl -i https://example.com
```

## Installation

### Build from source
```bash
git clone https://github.com/pynosaur/purl.git
cd purl
bazel build //:purl_bin
cp bazel-bin/purl ~/.local/bin/
```

### Development
```bash
# Run directly with Python
python app/main.py https://example.com

# Run tests
python test/test_main.py
```

## Testing

```bash
python test/test_main.py
python -m unittest discover -s test -v
```

