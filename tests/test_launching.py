import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from main import AppInfo, app_to_action_data


def test_app_to_action_data():
    app = AppInfo(
        name="系统",
        exec_command="gnome-control-center",
        desktop_path="/usr/share/applications/gnome-control-center.desktop",
    )
    data = app_to_action_data(app)
    assert data["exec_command"] == "gnome-control-center"
    assert (
        data["desktop_path"] == "/usr/share/applications/gnome-control-center.desktop"
    )
    assert data["name"] == "系统"


def test_action_data_round_trip():
    app = AppInfo(name="Test", exec_command="test-cmd", desktop_path="/test.desktop")
    data = app_to_action_data(app)
    assert data["exec_command"] == app.exec_command
    assert data["desktop_path"] == app.desktop_path
