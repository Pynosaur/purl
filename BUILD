genrule(
    name = "purl_bin",
    srcs = glob(["app/**/*.py", "doc/**/*.yaml"]),
    outs = ["purl"],
    cmd = """
        /opt/homebrew/bin/nuitka \
            --onefile \
            --include-data-dir=doc=doc \
            --onefile-tempdir-spec=/tmp/nuitka-purl \
            --no-progressbar \
            --assume-yes-for-downloads \
            --output-dir=$$(dirname $(location purl)) \
            --output-filename=purl \
            $(location app/main.py)
    """,
    local = 1,
    visibility = ["//visibility:public"],
)

