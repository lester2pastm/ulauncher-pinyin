from ulauncher.api.client.Extension import Extension
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction
from ulauncher.api.shared.action.ExtensionCustomAction import ExtensionCustomAction
from ulauncher.utils.desktopappinfo import DesktopAppInfo

import subprocess
import shlex
import gi
import importlib

gi.require_version("Gtk", "3.0")
Gtk = importlib.import_module("gi.repository.Gtk")


class PinyinExtension(Extension):
    def __init__(self):
        super(PinyinExtension, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        self.subscribe(ItemEnterEvent, ItemEnterEventListener())
        load_index()


class KeywordQueryEventListener:
    def on_event(self, event, extension) -> RenderResultListAction:
        # Get the query argument (everything after the keyword and space)
        argument = event.get_argument() or ""
        if not argument:
            return RenderResultListAction([])

        # Search all indexed apps for matches
        matches = search_apps(argument, all_apps)

        # Convert to extension result items
        items = [app_to_result_item(app) for app in matches[:8]]

        if not items:
            return RenderResultListAction([])

        return RenderResultListAction(items)


class ItemEnterEventListener:
    def on_event(self, event, extension) -> None:
        data = event.get_data()
        exec_cmd = data.get("exec_command", "")
        desktop_path = data.get("desktop_path", "")
        if exec_cmd:
            launch_app(exec_cmd, desktop_path)
        return None


from dataclasses import dataclass
from pathlib import Path
import configparser
import os

from pinyin_data import build_search_keys


# Module-level app index — loaded once when extension starts
all_apps = []


def load_index():
    global all_apps
    all_apps = load_all_apps()


DESKTOP_DIRS = [
    "/usr/share/applications",
    "/usr/local/share/applications",
    "/var/lib/flatpak/exports/share/applications",
]
user_dir = Path.home() / ".local" / "share" / "applications"
if user_dir.exists():
    DESKTOP_DIRS.append(str(user_dir))

flatpak_dir = Path("/var/lib/flatpak/app")
if flatpak_dir.exists():
    for item in flatpak_dir.iterdir():
        app_dir = item / "current" / "active" / "export" / "share" / "applications"
        if app_dir.exists():
            DESKTOP_DIRS.append(str(app_dir))


def resolve_icon(icon_name: str) -> str:
    if not icon_name:
        return "images/icon.png"
    if icon_name.startswith("/"):
        return icon_name
    icon_info = Gtk.IconTheme.get_default().lookup_icon(
        icon_name, ExtensionResultItem.get_icon_size(), Gtk.IconLookupFlags.FORCE_SIZE
    )
    if icon_info and icon_info.get_filename():
        return icon_info.get_filename()
    return "images/icon.png"


@dataclass
class AppInfo:
    name: str
    exec_command: str
    icon: str = ""
    no_display: bool = False
    keywords: str = ""
    comment: str = ""
    desktop_path: str = ""

    def to_search_record(self):
        return {
            "name": self.name,
            "exec": self.exec_command,
            "icon": self.icon,
            "keywords": self.keywords,
            "comment": self.comment,
            "no_display": self.no_display,
        }

    def build_search_keys(self):
        """Return a dict with searchable pinyin keys derived from the app name."""
        keys = build_search_keys(self.name)
        return {
            "original": self.name,
            "full_pinyin": keys["full_pinyin"],
            "initials": keys["initials"],
            "exec": self.exec_command,
            "icon": self.icon,
        }


def launch_app(exec_command: str, desktop_path: str = ""):
    """Launch an application by exec command."""
    try:
        args = shlex.split(exec_command)
        subprocess.Popen(
            args,
            start_new_session=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception as e:
        print(f"Failed to launch {exec_command}: {e}")


def app_to_action_data(app: AppInfo) -> dict:
    """Serialize app info for passing through ExtensionCustomAction."""
    return {
        "exec_command": app.exec_command,
        "desktop_path": app.desktop_path,
        "name": app.name,
    }


def app_to_result_item(app: AppInfo) -> ExtensionResultItem:
    return ExtensionResultItem(
        icon=resolve_icon(app.icon),
        name=app.name,
        description=app.comment,
        on_enter=ExtensionCustomAction(app_to_action_data(app), keep_app_open=False),
    )


def load_apps_from_paths(paths):
    apps = []
    seen_names = set()
    for path_str in paths:
        path = Path(path_str)
        if not path.exists():
            continue
        try:
            desktop_app = DesktopAppInfo.new_from_filename(path_str)
        except TypeError:
            continue
        if not desktop_app:
            continue
        cfg = configparser.ConfigParser(interpolation=None)
        try:
            cfg.read(path_str, encoding="utf-8")
        except Exception:
            continue
        if not cfg.has_section("Desktop Entry"):
            continue
        sec = cfg["Desktop Entry"]
        if sec.get("Type") != "Application":
            continue
        if sec.getboolean("NoDisplay", False) or desktop_app.get_nodisplay():
            continue
        name = desktop_app.get_name() or sec.get("Name", "")
        exec_cmd = desktop_app.get_string("Exec") or sec.get("Exec", "")
        comment = desktop_app.get_description() or ""
        if not comment and desktop_app.get_generic_name() != name:
            comment = desktop_app.get_generic_name() or ""
        if not name or not exec_cmd:
            continue
        if name in seen_names:
            continue
        seen_names.add(name)
        apps.append(
            AppInfo(
                name=name,
                exec_command=exec_cmd,
                icon=desktop_app.get_string("Icon") or sec.get("Icon", ""),
                keywords=sec.get("Keywords", ""),
                comment=comment,
                desktop_path=path_str,
            )
        )
    return apps


def load_all_apps():
    all_paths = []
    for d in DESKTOP_DIRS:
        if os.path.isdir(d):
            all_paths.extend(
                os.path.join(d, f) for f in os.listdir(d) if f.endswith(".desktop")
            )
    return load_apps_from_paths(all_paths)


def search_apps(query: str, apps: list[AppInfo]) -> list[AppInfo]:
    """
    Search apps by query string, matching against original name, full pinyin,
    and initials with deterministic ranking.

    Returns apps sorted by rank (highest priority first).
    Only apps with at least a substring match are returned.
    """
    if not query:
        return []

    query = query.lower()
    scored = []

    for app in apps:
        keys = app.build_search_keys()
        original = keys["original"]
        full = keys["full_pinyin"].lower()
        inits = keys["initials"].lower()

        rank = None

        # Rank 1: exact original
        if original == query:
            rank = 1
        # Rank 2: prefix original
        elif original.startswith(query):
            rank = 2
        # Rank 3: exact full pinyin
        elif full == query:
            rank = 3
        # Rank 4: prefix full pinyin
        elif full.startswith(query):
            rank = 4
        # Rank 5: exact initials
        elif inits == query:
            rank = 5
        # Rank 6: prefix initials
        elif inits.startswith(query):
            rank = 6
        # Rank 7: substring fallback
        elif query in full or query in original:
            rank = 7
        else:
            rank = None

        if rank is not None:
            scored.append((rank, full, inits, app))

    # Sort by rank, then by full_pinyin for ties
    scored.sort(key=lambda x: (x[0], x[1], x[2]))
    return [app for _, _, _, app in scored]


if __name__ == "__main__":
    load_index()
    PinyinExtension().run()
