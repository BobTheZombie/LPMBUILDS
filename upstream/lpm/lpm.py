"""Simplified LPM command line interface.

This module provides a ``buildpkg`` command that can generate wheels for
Python packages from PyPI.  It purposely avoids depending on a bundled
interpreter so that it can run both inside a PyInstaller one-file bundle
and directly from a system Python installation.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Iterable, Sequence


def _resolve_python_executable(explicit: str | None = None) -> str:
    """Return the Python interpreter that should be used for pip operations.

    Parameters
    ----------
    explicit:
        Optional path provided by the caller.  When supplied the path is
        returned verbatim.

    Returns
    -------
    str
        The path to a Python interpreter that can execute ``pip``.

    Raises
    ------
    RuntimeError
        If no suitable interpreter can be found.
    """

    if explicit:
        return explicit

    candidates: list[str | None] = []

    # Primary choice: whatever interpreter is currently running the CLI.
    executable = sys.executable
    if executable and os.path.exists(executable):
        candidates.append(executable)

    # Fallback: locate ``python3`` on the PATH.  This covers situations where
    # the PyInstaller one-file bootstrap interpreter lives outside the
    # unpacked bundle (e.g. provided by the ``python`` package in the LPM
    # environment).
    candidates.append(shutil.which("python3"))

    # As a last resort allow the generic ``python`` command.
    candidates.append(shutil.which("python"))

    for candidate in candidates:
        if not candidate or not os.path.exists(candidate):
            continue

        if (
            candidate == executable
            and getattr(sys, "frozen", False)
            and not os.path.basename(candidate).startswith("python")
        ):
            # ``sys.executable`` points at the PyInstaller launcher which is
            # not a usable interpreter for ``-m pip``.  Continue searching.
            continue

        return candidate

    searched = ", ".join(repr(c) for c in candidates)
    raise RuntimeError(
        "Unable to determine a Python interpreter; tried the following "
        f"candidates: {searched}"
    )


def build_python_package_from_pip(
    package: str,
    destination: os.PathLike[str] | str,
    *,
    python_executable: str | None = None,
    extra_pip_args: Sequence[str] | None = None,
    env: dict[str, str] | None = None,
) -> str:
    """Build a Python wheel for ``package`` using ``pip``.

    Parameters
    ----------
    package:
        Name of the package (any argument accepted by ``pip wheel``).
    destination:
        Directory that will receive the built wheel.
    python_executable:
        Optional override for the interpreter used to invoke ``pip``.
    extra_pip_args:
        Additional arguments forwarded to ``pip wheel``.
    env:
        Optional custom environment for the subprocess invocation.

    Returns
    -------
    str
        The interpreter used to run ``pip``.
    """

    interpreter = _resolve_python_executable(python_executable)
    output_dir = Path(destination)
    output_dir.mkdir(parents=True, exist_ok=True)

    cmd: list[str] = [interpreter, "-m", "pip", "wheel", package, "--no-deps", "-w", str(output_dir)]
    if extra_pip_args:
        cmd.extend(extra_pip_args)

    subprocess.run(cmd, check=True, env=env)
    return interpreter


def _add_buildpkg_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    buildpkg = subparsers.add_parser(
        "buildpkg",
        help="Build packages managed by LPM",
    )
    buildpkg.add_argument(
        "--python-pip",
        dest="python_pip",
        metavar="PACKAGE",
        help="Build a Python wheel using pip",
    )
    buildpkg.add_argument(
        "-o",
        "--output-dir",
        dest="output_dir",
        default="build/python",
        help="Directory where the built artifacts will be stored",
    )
    buildpkg.add_argument(
        "--python-executable",
        dest="python_executable",
        help="Explicit Python interpreter to run pip with",
    )
    buildpkg.add_argument(
        "--pip-arg",
        dest="pip_args",
        action="append",
        default=None,
        help="Extra arguments forwarded to pip wheel",
    )


def _buildpkg_command(args: argparse.Namespace) -> int:
    if not args.python_pip:
        raise SystemExit("buildpkg currently requires --python-pip")

    interpreter = build_python_package_from_pip(
        args.python_pip,
        args.output_dir,
        python_executable=args.python_executable,
        extra_pip_args=args.pip_args,
    )
    print(f"Built {args.python_pip} using interpreter: {interpreter}")
    return 0


def create_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="lpm")
    subparsers = parser.add_subparsers(dest="command")
    subparsers.required = True
    _add_buildpkg_parser(subparsers)
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    parser = create_argument_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)

    if args.command == "buildpkg":
        return _buildpkg_command(args)

    parser.error(f"Unhandled command: {args.command}")
    return 1


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    sys.exit(main())
