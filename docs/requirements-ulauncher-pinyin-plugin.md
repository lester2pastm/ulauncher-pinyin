# Ulauncher Pinyin Plugin Requirements

## Objective

Build a Ulauncher extension that lets the user search Chinese-named desktop applications by typing pinyin with a keyword trigger, for example `py xitong` matching an app named `系统`.

## Background

Ulauncher extensions cannot modify the built-in app search behavior. They can only react to input that starts with an extension-defined keyword. Because of this API boundary, the first deliverable is a keyword-triggered extension rather than a native replacement for default app search.

## Problem Statement

The current Ulauncher default search requires Chinese input to find many Chinese-named applications. The user wants a practical workaround that supports latinized pinyin input without changing Ulauncher's core search engine.

## Users

- Primary user: a Chinese-speaking Linux desktop user who uses Ulauncher as an application launcher.
- Secondary user: a developer evaluating whether the behavior is useful enough to later upstream into Ulauncher core.

## Success Criteria

- Typing `py xitong` shows a Chinese-named app such as `系统` when the app is present on the machine.
- Typing `py xt` can match the same app through acronym-style pinyin matching.
- Selecting a result launches the correct application.
- Query handling feels responsive for a normal desktop app set.
- The solution stays within Ulauncher extension API constraints.

## In Scope

- Ulauncher extension API v2 plugin structure.
- Keyword-triggered search via `KeywordQueryEvent`.
- Scanning local desktop application metadata from `.desktop` files.
- Building a lightweight in-memory search index.
- Matching against:
  - original Chinese app name
  - full pinyin
  - pinyin initials
- Rendering results with `ExtensionResultItem`.
- Launching selected apps from extension results.
- Basic logging and manual verification.

## Out of Scope

- Replacing Ulauncher's built-in app search.
- Global no-prefix search like plain `xitong`.
- General transliteration support for every writing system.
- Perfect fuzzy ranking from day one.
- Full test automation if the local environment cannot run Ulauncher integration flows yet.
- UI redesign or custom extension preferences beyond what is needed for the MVP.

## Functional Requirements

### FR1 - Keyword Trigger

The extension must define a keyword, initially `py`, and only process queries that start with that keyword.

### FR2 - App Discovery

The extension must discover launchable desktop apps from standard Linux `.desktop` file locations.

### FR3 - Search Index

For each app, the extension must retain enough data to:

- display app name
- show an icon if available
- launch the app
- match against original name and pinyin-derived forms

### FR4 - Pinyin Matching

The extension must support at least:

- exact and prefix matching on full pinyin
- exact and prefix matching on pinyin initials
- exact and prefix matching on original app name

### FR5 - Result Rendering

The extension must render a result list in Ulauncher using supported extension result items and actions.

### FR6 - Result Activation

When the user selects a result, the associated application must launch reliably.

## Non-Functional Requirements

### NFR1 - API Compliance

The extension must only use documented Ulauncher extension APIs and packaging structure.

### NFR2 - Dependency Strategy

The extension must not assume Ulauncher can install arbitrary Python dependencies on behalf of the extension. Any pinyin support must be implemented in a distribution-safe way for the extension.

### NFR3 - Performance

The extension should avoid rebuilding the full app index on every keystroke.

### NFR4 - Simplicity

The MVP should prefer a small, understandable implementation over a highly abstract design.

## Constraints

- Workspace starts empty; all plugin files will be created from scratch.
- Ulauncher extension docs indicate at least one `keyword` preference is required in `manifest.json`.
- Extensions run as separate Python processes and return results through `RenderResultListAction`.
- Built-in Ulauncher app search cannot be intercepted by an extension.

## MVP Technical Assumptions

- The extension will target Ulauncher Extension API v2.
- The initial implementation may keep indexing and matching logic inside `main.py` to reduce moving parts.
- Search matching can start with deterministic prefix and substring logic before introducing more advanced ranking.

## Open Decisions

- Which pinyin conversion strategy to bundle into the plugin.
- Whether to use `LaunchAppAction` directly or a custom activation path after validating behavior on the target machine.
- Whether to include description and keyword fields in v1 matching or defer them until after the MVP works.

## Acceptance Scenarios

1. User opens Ulauncher and types `py xitong`.
2. Extension returns a result representing a Chinese app named `系统`.
3. User selects the result.
4. The application launches.

Additional scenario:

1. User types `py xt`.
2. Extension returns `系统` through initial-letter matching.
