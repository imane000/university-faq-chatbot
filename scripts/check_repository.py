"""Heuristic Git secret/artifact scan. Findings contain paths, never secret values.

Run after staging: python scripts/check_repository.py --history
This complements provider secret scanning and manual review; it is not a guarantee.
"""

import argparse
import io
import re
import subprocess
from pathlib import Path

PATTERNS = {
    "provider token": re.compile(rb"(?:gsk_|sk-(?:proj-)?|gh[pousr]_)[A-Za-z0-9_-]{20,}"),
    "AWS access key": re.compile(rb"(?:AKIA|ASIA)[A-Z0-9]{16}"),
    "private key": re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "credential URL": re.compile(rb"https?://[^\s/:]+:[^\s/@]+@"),
    "assigned credential": re.compile(
        rb"""(?i)(?:api_key|secret_key|access_token|password)\s*[=:]\s*["'][A-Za-z0-9_+/=-]{24,}["']"""
    ),
}


def git(*args: str) -> bytes:
    return subprocess.check_output(["git", *args])


def scan(data: bytes, path: str) -> set[str]:
    hits = {label for label, pattern in PATTERNS.items() if pattern.search(data)}
    if path.lower().endswith(".pdf"):
        from pypdf import PdfReader

        text = "\n".join(page.extract_text() or "" for page in PdfReader(io.BytesIO(data)).pages)
        hits |= {label for label, pattern in PATTERNS.items() if pattern.search(text.encode())}
    return hits


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--history", action="store_true")
    args = parser.parse_args()
    findings = set()
    paths = git("ls-files", "-z").decode().split("\0")
    for name in filter(None, paths):
        path = Path(name)
        if not path.is_file():
            continue
        if (path.name.startswith(".env") and path.name != ".env.example") or (
            "chroma_db" in path.parts
            or "node_modules" in path.parts
            or path.suffix in {".sqlite", ".sqlite3", ".pem", ".key"}
        ):
            findings.add((name, "generated or sensitive artifact tracked"))
        findings.update((name, label) for label in scan(path.read_bytes(), name))
    count = 0
    if args.history:
        for row in git("rev-list", "--objects", "--all").decode().splitlines():
            sha, _, path = row.partition(" ")
            if not path or git("cat-file", "-t", sha).strip() != b"blob":
                continue
            count += 1
            findings.update(
                (path, f"history: {label}") for label in scan(git("cat-file", "blob", sha), path)
            )
    for path, label in sorted(findings):
        print(f"{path}: {label}")
    print(f"Scanned tracked files and {count} historical blobs; {len(findings)} findings.")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
