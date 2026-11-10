"""Platform-aware locations of PCSX2's user data (settings, logs)."""

from __future__ import annotations

import os
import sys
from pathlib import Path

IS_WINDOWS = sys.platform == "win32"


def data_dirs() -> list[Path]:
    """Candidate PCSX2 user data directories, most likely first.

    Override with the PCSX2_MCP_DATA_DIR environment variable.
    """
    override = os.environ.get("PCSX2_MCP_DATA_DIR")
    if override:
        return [Path(override).expanduser()]
    if IS_WINDOWS:
        docs = Path.home() / "Documents" / "PCSX2"
        local = Path(os.environ.get("LOCALAPPDATA", str(Path.home() / "AppData/Local"))) / "PCSX2"
        return [docs, local]
    if sys.platform == "darwin":
        return [Path.home() / "Library" / "Application Support" / "PCSX2"]
    xdg = Path(os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config")
    return [
        xdg / "PCSX2",
        Path.home() / ".var" / "app" / "net.pcsx2.PCSX2" / "config" / "PCSX2",  # Flatpak
    ]


def primary_data_dir() -> Path:
    dirs = data_dirs()
    return next((d for d in dirs if d.exists()), dirs[0])


def config_candidates() -> list[Path]:
    out: list[Path] = []
    for d in data_dirs():
        out += [d / "inis" / "PCSX2.ini", d / "PCSX2.ini"]
    # Prefer inis/PCSX2.ini (the modern layout) when the directory has one.
    return out


def log_candidates() -> list[Path]:
    out: list[Path] = []
    for d in data_dirs():
        out += [d / "logs" / "emulog.txt", d / "logs" / "pcsx2.log", d / "emulog.txt", d / "pcsx2.log"]
    return out


class Unavailable:
    """Stand-in for a module that cannot load on this platform.

    Any attribute access returns a callable that raises OSError, which the
    server's tools already catch and report as a normal error result.
    """

    def __init__(self, feature: str, reason: BaseException) -> None:
        self._feature = feature
        self._reason = reason

    def __getattr__(self, name: str):
        def _raise(*_args, **_kwargs):
            raise OSError(f"{self._feature} is not supported on {sys.platform} ({self._reason})")

        return _raise
