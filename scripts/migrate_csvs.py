"""Run ukrdc-sqla's CSV migration tool (migration_tool/csv_migrate.py) from this repo.

All this script does is find the tool, then run the tool's own CLI with
--models ukrdc_sqla.ukrdc:Base and --steps <ukrdc-sqla>/migrations/ukrdc/csv_steps
filled in. Everything after the script name is the tool's own command line:

    poetry run python scripts/migrate_csvs.py --help
    poetry run python scripts/migrate_csvs.py init tables --step base
    poetry run python scripts/migrate_csvs.py stamp tables Facility tables/facility_new/facilities.csv --step base
    poetry run python scripts/migrate_csvs.py current tables
    poetry run python scripts/migrate_csvs.py upgrade tables
    poetry run python scripts/migrate_csvs.py history

The tool comes from a checkout of ukrdc-sqla at the commit poetry.lock resolved to (or
tag v<version> for a PyPI install), kept in .ukrdc-sqla/ and cloned on first use. Set
UKRDC_SQLA_PATH to use your own ukrdc-sqla checkout instead.
"""

from __future__ import annotations

import importlib.util
import os
import re
import shutil

# subprocess only runs git (by its full path), with arguments built in this script.
import subprocess  # nosec B404
import sys
from pathlib import Path
from typing import NoReturn

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / ".ukrdc-sqla"
REPO = "https://github.com/renalreg/ukrdc-sqla.git"
MODELS = "ukrdc_sqla.ukrdc:Base"


def fail(message: str) -> NoReturn:
    sys.exit(f"migrate_csvs: {message}")


def locked_ref() -> str:
    """The git ref of ukrdc-sqla in poetry.lock: the resolved commit, or v<version>."""
    lock_file = ROOT / "poetry.lock"
    if not lock_file.exists():
        fail(f"{lock_file} not found: run poetry lock first.")
    lock = lock_file.read_text(encoding="utf-8")
    for block in re.split(r"^\[\[package\]\]$", lock, flags=re.MULTILINE):
        if re.search(r'^name = "ukrdc-sqla"$', block, re.MULTILINE):
            sha = re.search(
                r'^resolved_reference = "([0-9a-f]+)"$', block, re.MULTILINE
            )
            version = re.search(r'^version = "([^"]+)"$', block, re.MULTILINE)
            if sha:
                return sha[1]
            if version:
                return f"v{version[1]}"
    fail("ukrdc-sqla isn't in poetry.lock: run poetry lock first.")


def git_path() -> str:
    path = shutil.which("git")
    if not path:
        fail("git isn't installed (or isn't on PATH).")
    return path


def git(*args: str) -> None:
    result = subprocess.run(  # nosec B603
        [git_path(), *args], capture_output=True, text=True, check=False
    )
    if result.returncode:
        fail(f"git {' '.join(args)} failed:\n{result.stderr.strip()}")


def commit_of(repo: Path, ref: str) -> str | None:
    result = subprocess.run(  # nosec B603
        [
            git_path(),
            "-C",
            str(repo),
            "rev-parse",
            "--verify",
            "--quiet",
            f"{ref}^{{commit}}",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout.strip() or None


def ukrdc_sqla_checkout() -> Path:
    """UKRDC_SQLA_PATH, or .ukrdc-sqla/ at the ref in poetry.lock."""
    if os.environ.get("UKRDC_SQLA_PATH"):
        return Path(os.environ["UKRDC_SQLA_PATH"]).resolve()
    ref = locked_ref()
    if not (CACHE / ".git").exists():
        print(f"migrate_csvs: cloning ukrdc-sqla into {CACHE} ...", file=sys.stderr)
        git("clone", "--quiet", "--filter=blob:none", "--no-checkout", REPO, str(CACHE))
    if not commit_of(CACHE, ref):
        git("-C", str(CACHE), "fetch", "--quiet", "--tags", "origin")
    if not commit_of(CACHE, ref):  # a commit no branch points at any more
        git("-C", str(CACHE), "fetch", "--quiet", "origin", ref)
    if not commit_of(CACHE, ref):
        fail(f"can't find {ref} in {REPO}.")
    if commit_of(CACHE, "HEAD") != commit_of(CACHE, ref):
        git("-C", str(CACHE), "checkout", "--quiet", "--detach", ref)
    return CACHE


def main() -> None:
    checkout = ukrdc_sqla_checkout()
    tool = checkout / "migration_tool" / "csv_migrate.py"
    if not tool.exists():
        fail(f"{tool} not found.")
    spec = importlib.util.spec_from_file_location("csv_migrate", tool)
    if spec is None or spec.loader is None:
        fail(f"can't load {tool}.")
    csv_migrate = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(csv_migrate)
    steps = checkout / "migrations" / "ukrdc" / "csv_steps"
    csv_migrate.cli.main(
        args=["--models", MODELS, "--steps", str(steps), *sys.argv[1:]],
        prog_name="migrate_csvs.py",
    )


if __name__ == "__main__":
    main()
