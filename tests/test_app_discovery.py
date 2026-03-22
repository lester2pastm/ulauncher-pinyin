import pytest
import tempfile
from pathlib import Path

# Adjust import path once structure is in place
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from main import load_apps_from_paths, AppInfo


def test_parse_desktop_entry(tmp_path):
    """A valid desktop entry with Chinese name is parsed correctly."""
    desktop = tmp_path / "system.desktop"
    desktop.write_text(
        "[Desktop Entry]\nName=系统\nExec=gnome-control-center\nIcon=gnome-control-center\nType=Application\n",
        encoding="utf-8",
    )
    apps = load_apps_from_paths([str(desktop)])
    assert len(apps) == 1
    assert apps[0].name == "系统"
    assert apps[0].exec_command == "gnome-control-center"
    assert apps[0].icon == "gnome-control-center"


def test_skip_nodisplay_app(tmp_path):
    """An app with NoDisplay=true is skipped."""
    desktop = tmp_path / "hidden.desktop"
    desktop.write_text(
        "[Desktop Entry]\nName=Hidden App\nExec=hidden-cmd\nNoDisplay=true\nType=Application\n",
        encoding="utf-8",
    )
    apps = load_apps_from_paths([str(desktop)])
    # NoDisplay apps should be excluded
    assert all(a.name != "Hidden App" for a in apps)


def test_skip_invalid_entry(tmp_path):
    """A file that is not a desktop entry is skipped gracefully."""
    txt = tmp_path / "readme.txt"
    txt.write_text("This is not a desktop file", encoding="utf-8")
    apps = load_apps_from_paths([str(txt)])
    assert len(apps) == 0
