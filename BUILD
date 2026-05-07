genrule(
    name = "purl_bin",
    srcs = glob(["app/**/*.py", "doc/**/*.yaml"]) + [".program"],
    outs = ["purl"],
    cmd = """
        _VER=$$(grep '^version:' $(location .program) | cut -d' ' -f2)
        /opt/homebrew/bin/nuitka \
            --onefile \
            --include-data-dir=doc=doc \
            --onefile-tempdir-spec=/tmp/nuitka-purl-$$_VER \
            --no-progressbar \
            --assume-yes-for-downloads \
            --output-dir=$$(dirname $(location purl)) \
            --output-filename=purl \
            $(location app/main.py)
    """,
    local = 1,
    visibility = ["//visibility:public"],
)

