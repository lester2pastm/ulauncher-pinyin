import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from main import AppInfo, app_to_result_item, search_apps
from ulauncher.search.Query import Query


def test_exact_original_match_ranks_first():
    """Exact original name match should be top result."""
    apps = [
        AppInfo(name="系统", exec_command="gnome-control-center"),
        AppInfo(name="xits", exec_command="other-cmd"),
    ]
    results = search_apps("系统", apps)
    assert results[0].name == "系统"


def test_prefix_original_match_ranks_above_pinyin():
    """Prefix original match should rank above full pinyin match."""
    apps = [
        AppInfo(name="系统", exec_command="ctrl"),
        AppInfo(name="xitong-tools", exec_command="other"),
    ]
    results = search_apps("系统", apps)
    assert results[0].name == "系统"


def test_full_pinyin_exact_match():
    """Full pinyin exact match should work."""
    apps = [
        AppInfo(name="系统", exec_command="ctrl"),
    ]
    results = search_apps("xitong", apps)
    assert len(results) >= 1
    assert results[0].name == "系统"


def test_full_pinyin_prefix_match():
    """Full pinyin prefix match should work."""
    apps = [
        AppInfo(name="系统", exec_command="ctrl"),
        AppInfo(name="xyz", exec_command="other"),
    ]
    results = search_apps("xito", apps)
    assert len(results) >= 1
    assert results[0].name == "系统"


def test_initials_match():
    """Initials match should work."""
    apps = [
        AppInfo(name="系统", exec_command="ctrl"),
    ]
    results = search_apps("xt", apps)
    assert len(results) >= 1
    assert results[0].name == "系统"


def test_full_pinyin_match_for_lanxin():
    apps = [
        AppInfo(name="蓝信", exec_command="lanxin"),
    ]
    results = search_apps("lanxin", apps)
    assert len(results) >= 1
    assert results[0].name == "蓝信"


def test_initials_match_for_lanxin():
    apps = [
        AppInfo(name="蓝信", exec_command="lanxin"),
    ]
    results = search_apps("lx", apps)
    assert len(results) >= 1
    assert results[0].name == "蓝信"


def test_no_match_returns_empty():
    """Query with no match should return empty list."""
    apps = [
        AppInfo(name="Chrome", exec_command="chrome"),
    ]
    results = search_apps("xyzxyz", apps)
    assert results == []


def test_empty_query_returns_empty():
    """Empty query should return empty list."""
    apps = [AppInfo(name="系统", exec_command="ctrl")]
    results = search_apps("", apps)
    assert results == []


def test_result_item_keeps_empty_description_when_comment_missing():
    app = AppInfo(name="腾讯会议", exec_command="wemeetapp", comment="")

    item = app_to_result_item(app)

    assert item.get_description(Query("py tengxun")) == ""
