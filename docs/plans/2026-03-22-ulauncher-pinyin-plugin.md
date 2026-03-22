# Ulauncher Pinyin Plugin Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a Ulauncher extension that supports keyword-triggered pinyin search for Chinese-named desktop applications and launches selected apps.

**Architecture:** Use a standard Ulauncher extension skeleton with a keyword-triggered entry point in `main.py`. Build an in-memory app index from `.desktop` files, derive original-name and pinyin-based search keys, then return Ulauncher result items for matching apps. Keep the MVP implementation concentrated and simple, then refactor only after the flow works.

**Tech Stack:** Python 3, Ulauncher Extension API v2, Linux desktop `.desktop` metadata parsing, bundled pinyin conversion logic, pytest-style tests where feasible.

---

## Preconditions

- Read `docs/requirements-ulauncher-pinyin-plugin.md` before changing code.
- Verify the installed Ulauncher version supports Extension API v2.
- Confirm the local machine has standard desktop app metadata available under common Linux application directories.

### Task 1: Create plugin skeleton

**Files:**
- Create: `manifest.json`
- Create: `versions.json`
- Create: `main.py`
- Create: `images/icon.png`

**Step 1: Write the manifest file**

Create `manifest.json` with:

- `required_api_version`
- extension name and description
- `icon`
- `query_debounce`
- a `keyword` preference with default value `py`

**Step 2: Write the versions file**

Create `versions.json` mapping API version `2` to the working branch.

**Step 3: Write minimal extension entry point**

Create `main.py` with:

- `Extension` subclass
- `KeywordQueryEvent` subscription
- minimal event listener returning one fixed result item

**Step 4: Manual verification**

Install or symlink the extension into `~/.local/share/ulauncher/extensions/`.

Run Ulauncher, type `py test`, and verify one dummy result appears.

**Step 5: Commit**

```bash
git add manifest.json versions.json main.py images/icon.png
git commit -m "feat: scaffold ulauncher pinyin extension"
```

### Task 2: Add app discovery

**Files:**
- Modify: `main.py`
- Create: `tests/test_app_discovery.py`

**Step 1: Write the failing test**

Add a test that builds a temporary `.desktop` file and expects the parser to return:

- app name
- executable command
- icon name or path
- visibility status

Example:

```python
def test_parse_desktop_entry(tmp_path):
    desktop = tmp_path / "system.desktop"
    desktop.write_text(
        "[Desktop Entry]\nName=系统\nExec=gnome-control-center\nType=Application\n",
        encoding="utf-8",
    )
    apps = load_apps_from_paths([desktop])
    assert apps[0].name == "系统"
    assert apps[0].exec_command == "gnome-control-center"
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_app_discovery.py::test_parse_desktop_entry -v`

Expected: FAIL because loader does not exist yet.

**Step 3: Write minimal implementation**

Add app discovery helpers to `main.py` that:

- inspect common application directories
- parse `.desktop` files safely
- skip invalid or hidden entries

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_app_discovery.py::test_parse_desktop_entry -v`

Expected: PASS.

**Step 5: Manual verification**

Temporarily log discovered app count when the plugin starts.

**Step 6: Commit**

```bash
git add main.py tests/test_app_discovery.py
git commit -m "feat: load desktop applications for search"
```

### Task 3: Add bundled pinyin key generation

**Files:**
- Modify: `main.py`
- Create: `tests/test_pinyin_keys.py`
- Create or vendor: `vendor/` or `pinyin_data.py`

**Step 1: Write the failing test**

Add tests for deriving search keys from Chinese names.

```python
def test_build_search_keys_for_chinese_name():
    keys = build_search_keys("系统")
    assert "系统" in keys.original
    assert "xitong" in keys.full_pinyin
    assert "xt" in keys.initials
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_pinyin_keys.py::test_build_search_keys_for_chinese_name -v`

Expected: FAIL because the builder does not exist yet.

**Step 3: Write minimal implementation**

Add a bundled pinyin strategy that works without relying on extension-side dependency installation.

Requirements:

- convert Chinese names into full pinyin
- derive initials
- preserve original name for direct script matching

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_pinyin_keys.py::test_build_search_keys_for_chinese_name -v`

Expected: PASS.

**Step 5: Commit**

```bash
git add main.py tests/test_pinyin_keys.py vendor pinyin_data.py
git commit -m "feat: add bundled pinyin search keys"
```

### Task 4: Implement query matching and ranking

**Files:**
- Modify: `main.py`
- Create: `tests/test_matching.py`

**Step 1: Write the failing tests**

Add tests that verify ranking order.

```python
def test_full_pinyin_prefix_match_beats_initials():
    apps = [
        IndexedApp(name="系统", full_pinyin="xitong", initials="xt"),
        IndexedApp(name="协调器", full_pinyin="xietiaoqi", initials="xtq"),
    ]
    results = search_apps("xit", apps)
    assert results[0].name == "系统"
```

Also add tests for:

- original Chinese query match
- initials match
- empty query behavior

**Step 2: Run tests to verify they fail**

Run: `pytest tests/test_matching.py -v`

Expected: FAIL because ranking logic is incomplete.

**Step 3: Write minimal implementation**

Implement deterministic ranking:

- exact original match
- original prefix match
- full pinyin exact match
- full pinyin prefix match
- initials exact match
- initials prefix match
- optional substring fallback

**Step 4: Run tests to verify they pass**

Run: `pytest tests/test_matching.py -v`

Expected: PASS.

**Step 5: Commit**

```bash
git add main.py tests/test_matching.py
git commit -m "feat: rank results by pinyin and original name"
```

### Task 5: Render real extension results

**Files:**
- Modify: `main.py`

**Step 1: Replace dummy query handler**

Update the keyword event listener to:

- read the query argument
- search the indexed apps
- convert matches into `ExtensionResultItem` objects

Each result should include:

- app name
- optional description or launch command hint
- icon when resolvable

**Step 2: Manual verification**

Restart Ulauncher.

Type:

- `py 系统`
- `py xitong`
- `py xt`

Expected: matching app results appear.

**Step 3: Commit**

```bash
git add main.py
git commit -m "feat: render pinyin search results in ulauncher"
```

### Task 6: Launch selected apps

**Files:**
- Modify: `main.py`
- Create: `tests/test_launching.py`

**Step 1: Write the failing test**

If launch logic is factored into a helper, add a test for transforming the selected app into a launchable action or command.

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_launching.py -v`

Expected: FAIL because launch handling is not implemented.

**Step 3: Write minimal implementation**

Use the most reliable activation path available after local verification:

- prefer documented Ulauncher launch action if it behaves correctly for discovered apps
- otherwise use `ExtensionCustomAction` and handle launch in `ItemEnterEvent`

**Step 4: Run tests to verify they pass**

Run: `pytest tests/test_launching.py -v`

Expected: PASS.

**Step 5: Manual verification**

Select a Chinese-named app result in Ulauncher and verify the app launches.

**Step 6: Commit**

```bash
git add main.py tests/test_launching.py
git commit -m "feat: launch apps from pinyin search results"
```

### Task 7: Add caching and polish only if needed

**Files:**
- Modify: `main.py`
- Create: `tests/test_cache_behavior.py`

**Step 1: Observe performance before optimizing**

Measure whether rebuilding the app index on each query is noticeably slow.

**Step 2: Write the failing test**

If caching is needed, add a test that ensures index reuse between repeated queries.

**Step 3: Write minimal implementation**

Cache app index in memory and refresh only when necessary.

**Step 4: Verify behavior**

Run targeted tests and manually check repeated queries.

**Step 5: Commit**

```bash
git add main.py tests/test_cache_behavior.py
git commit -m "perf: cache app index for repeated queries"
```

### Task 8: Final verification

**Files:**
- Verify: `manifest.json`
- Verify: `versions.json`
- Verify: `main.py`
- Verify: `tests/`

**Step 1: Run the focused test suite**

Run: `pytest tests -v`

Expected: PASS for the plugin test suite.

**Step 2: Manual end-to-end verification**

Check all MVP scenarios:

- `py xitong`
- `py xt`
- `py 系统`
- result activation
- no obvious lag while typing

**Step 3: Review for API compliance**

Confirm the plugin still uses only keyword-triggered extension flow and documented actions/events.

**Step 4: Commit**

```bash
git add .
git commit -m "test: verify mvp ulauncher pinyin extension"
```

## Notes for Implementation

- Keep the MVP focused on Chinese app names only.
- Avoid building a generic multilingual transliteration engine in v1.
- Do not refactor into multiple modules until the full flow is working.
- If local Ulauncher behavior differs from docs for any action class, prefer the behavior proven by local testing.
