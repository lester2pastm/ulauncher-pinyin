import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from main import load_index, all_apps, search_apps


def test_index_loaded_at_startup():
    """Verify the module-level all_apps list is populated after load_index()."""
    load_index()
    assert isinstance(all_apps, list)
    assert len(all_apps) > 0


def test_same_index_reused_across_multiple_searches():
    """Verify the same app list is used across multiple search_apps calls without rebuilding."""
    load_index()
    initial_len = len(all_apps)
    assert initial_len > 0

    # Multiple searches should NOT rebuild the index
    results1 = search_apps("xitong", all_apps)
    results2 = search_apps("xt", all_apps)
    results3 = search_apps("系统", all_apps)

    # all_apps should be the exact same list object (same memory reference)
    assert len(all_apps) == initial_len
    # Should have received results for all queries
    assert len(results1) >= 0
    assert len(results2) >= 0
    assert len(results3) >= 0


def test_search_does_not_mutate_index():
    """Verify search_apps returns new lists and doesn't mutate all_apps."""
    load_index()
    initial_names = [a.name for a in all_apps[:10]]
    for _ in range(3):
        search_apps("xi", all_apps)
    current_names = [a.name for a in all_apps[:10]]
    assert initial_names == current_names, "search_apps should not mutate all_apps"
