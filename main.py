from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction


class PinyinExtension(Extension):
    def __init__(self):
        super(PinyinExtension, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())


class KeywordQueryEventListener(EventListener):
    def on_event(self, event, extension):
        items = []
        items.append(
            ExtensionResultItem(
                icon="images/icon.png",
                name="Test Item",
                description="Skeleton works",
                on_enter=HideWindowAction(),
            )
        )
        return RenderResultListAction(items)


if __name__ == "__main__":
    PinyinExtension().run()


from dataclasses import dataclass
from pathlib import Path
import configparser
import os

from pinyin_data import build_search_keys


DESKTOP_DIRS = [
    "/usr/share/applications",
    "/usr/local/share/applications",
]
user_dir = Path.home() / ".local" / "share" / "applications"
if user_dir.exists():
    DESKTOP_DIRS.append(str(user_dir))


@dataclass
class AppInfo:
    name: str
    exec_command: str
    icon: str = ""
    no_display: bool = False
    keywords: str = ""
    comment: str = ""

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


def load_apps_from_paths(paths):
    apps = []
    for path_str in paths:
        path = Path(path_str)
        if not path.exists():
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
        if sec.getboolean("NoDisplay", False):
            continue
        name = sec.get("Name", "")
        exec_cmd = sec.get("Exec", "")
        if not name or not exec_cmd:
            continue
        apps.append(
            AppInfo(
                name=name,
                exec_command=exec_cmd,
                icon=sec.get("Icon", ""),
                keywords=sec.get("Keywords", ""),
                comment=sec.get("Comment", ""),
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
