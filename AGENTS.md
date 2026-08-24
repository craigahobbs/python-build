# AGENTS.md

Notes for coding agents working **in this repository**. Downstream packages that *include* python-build should follow [SKILL.md](SKILL.md), not this file.

python-build is a GNU Make build system. The makefiles *are* the product — there is no Python package here. This repo's own `Makefile` is a snapshot-test harness; it does not `include Makefile.base`.

## Deliverables

| File | Role |
| --- | --- |
| `Makefile.base` | Build system consumers `include`. Targets: `test`, `lint`, `doc`, `cover`, `commit`, `publish`, `changelog`, `gh-pages`, `clean`, `superclean` |
| `Makefile.tool` | Lighter variant for non-package tool repos |
| `pylintrc` | Shared pylint config (no snapshot tests; consumers re-download it) |
| `SKILL.md` | Agent playbook for **downstream** packages |
| `README.md` | Human reference for targets and variables |

Consumer stubs wget `Makefile.base` / `pylintrc` / `Makefile.tool` from GitHub Pages, or copy them from `../python-build` when that tree exists. Downstream agents load `SKILL.md` from `../python-build/SKILL.md` if that file exists, otherwise from `https://raw.githubusercontent.com/craigahobbs/python-build/main/SKILL.md`. This repo's `make gh-pages` is a no-op; do not assume a make target publishes Pages.

`index.html` is a MarkdownUp shell for the README. Leave it unless the user asks.

## Commands

| Target | Purpose |
| --- | --- |
| `make test` | Run every snapshot fixture |
| `make test-<name>` | One fixture (`tests/<name>/`, e.g. `make test-commit`) |
| `make commit` | `test` only |
| `make clean` | `build/` and `test-actual/` |
| `make changelog` | Rewrite `CHANGELOG.md` via a local simple-git-changelog venv |

Do not run `make changelog` unless asked. There is no `cover` / `lint` / `publish` in *this* Makefile.

## Tests

Snapshots of `make -n` (dry-run command text), not of execution.

1. Fixture `tests/<name>/Makefile` sets placeholder versions (`python:3.X`, `X.Y.*`) and `include ../../Makefile.base` (or `Makefile.tool` for `tool-*`).
2. `TEST_RULE` in the top-level Makefile runs `make -C tests/<name>/ -n …`, rewrites `make[2]` → `make[X]` in "Nothing to be done" lines, and diffs `test-actual/<name>.txt` against `test-expected/<name>.txt`.
3. Checked-in empty venv markers skip venv-creation recipes in the dry run:
   - `build/venv/system.build` — default venv
   - `build/venv/system-util.build` — `-util` venv (`publish`, `changelog`)
   - `build/env.build` — `Makefile.tool` venv
4. `-2` fixtures pair with the unmarked fixture: unmarked shows venv creation (`tests/test/`), `-2` has the marker and does not (`tests/test-2/`). `publish` has `system.build` only (shows util-venv creation); `publish-2` has both markers.
5. On failure, `test-actual/<name>.txt` is left in place. If the change is intentional, copy it to `test-expected/<name>.txt` in the same commit. Never commit `test-actual/`.
6. To add a test: fixture Makefile (+ markers as needed), `$(eval $(call TEST_RULE, <name>, <goal and vars>))` in the top-level Makefile, and `test-expected/<name>.txt`.
7. The top-level Makefile sets `OS := Unknown` and unexports `USE_DOCKER` / `USE_PODMAN` so output is platform-stable. Do not remove that.

Fixtures override `PYTHON_IMAGES` to `python:3.X python:3.Y`. Changing the default image list in `Makefile.base` does not update snapshots; it still needs a README update when user-facing.

`commit-overrides` / `commit-overrides-unittest-parallel` are the pass-through tests for make variables. New variables that appear in recipes should show up there.

## `Makefile.base`

- System Python by default (`PYTHON_IMAGES := system`). `USE_DOCKER=1` / `USE_PODMAN=1` switches to official `python:X.Y` images; `VENV_RUN_FN` wraps recipes in `docker run` / `podman run`.
- `VENV_RULE_FN` — one venv per image under `build/venv/<image-name>` with a `.build` marker.
- `VENV_COMMAND_FN` — per-image phony (e.g. `test-python-3-13`) plus aggregate (`test`). `IMAGE_NAME_FN` maps `python:3.13` → `python-3-13`.
- First image is the default: `cover`, `lint`, `doc`, and `publish` run only there; other images run tests only. A separate `-util` venv holds build, twine, and simple-git-changelog.
- `publish-<default-image>-util` depends on `commit` so parallel `make -j publish` cannot upload before tests finish. Do not drop that.
- Recipe bodies pass through `$(call)` / `$(eval)`: `$$` defers one expansion level, `$$$$` two. This is the easiest thing to break.
- Pre-include variables (`PYTHON_IMAGES`, `SPHINX_DOC`, `GHPAGES_SRC`, `UNITTEST_PARALLEL`, …) are read at include time. Changing when they are expanded can silently ignore consumer Makefiles.
- Pinned versions (`COVERAGE_VERSION`, `PYLINT_VERSION`, `SPHINX_VERSION`, `UNITTEST_PARALLEL_VERSION`) sit near the top of `Makefile.base`. Bump them only with the expected files that print those strings.
- Windows: `VENV_BIN` / `VENV_PYTHON` become `Scripts` / `python.exe` when not using containers. Tests force `OS := Unknown`, so do not delete the Windows branches as unused.

GNU Make (`makefile-gmake`). Keep the MIT license header.

## `Makefile.tool`

Empty `test` / `lint` / `gh-pages`; `commit` = `test` + `lint`; venv at `build/env` from `TESTS_REQUIRE`. Tool fixtures extend `test`/`lint` like a consumer would. `PYTHON_IMAGE` (singular) is the container image, not `PYTHON_IMAGES`.

## Docs

| Change | Also update |
| --- | --- |
| User-facing target, variable, or stub Makefile | `README.md` and the matching snapshot(s) |
| Downstream agent workflow (`make test`, `TEST=`, coverage gate, `TESTS_REQUIRE`, …) | `SKILL.md` |
| Snapshot command text | `test-expected/<name>.txt` (same commit) |

Do not copy the README variable catalog into `SKILL.md` or this file.

## Do not

- Apply [SKILL.md](SKILL.md) here (`make cover`, pytest bans, `src/tests` layout). That skill is for consumers.
- Add Python package layout, pytest, or a second test runner.
- Rewrite consumer WGET stubs in the README unless the download contract changes.
- Hand-edit `CHANGELOG.md`; use `make changelog` when asked.
