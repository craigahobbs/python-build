# CLAUDE.md

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

Consumer stubs wget `Makefile.base` / `pylintrc` / `Makefile.tool` from GitHub Pages, or copy them from `../python-build` when that tree exists. Downstream agents load `SKILL.md` from `../python-build/SKILL.md` if that file exists, otherwise from `https://raw.githubusercontent.com/craigahobbs/python-build/main/SKILL.md`. This repo's `make gh-pages` is a no-op; do not assume a make target publishes Pages. GitHub Pages serves the `main` branch root, so a push to `main` publishes `Makefile.base` / `Makefile.tool` / `pylintrc` to every consumer's next download — run `make test` before pushing.

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
2. `TEST_RULE` in the top-level Makefile runs `make -C tests/<name>/ -n …`, rewrites `make[N]` → `make[X]` and the opening backtick → `'` in "Nothing to be done" lines (so output matches GNU Make 3.81 and 4.x), and diffs `test-actual/<name>.txt` against `test-expected/<name>.txt`.
3. Checked-in empty venv markers skip venv-creation recipes in the dry run:
   - `build/venv/system.build` — default venv
   - `build/venv/system-util.build` — `-util` venv (`publish`, `changelog`)
   - `build/env.build` — `Makefile.tool` venv
4. Pairs `<x>` / `<x>-2` (test, cover, doc, lint, publish, test-unittest-parallel, tool-commit): `<x>` shows venv creation, `<x>-2` has the marker and does not. `publish` has `system.build` only (shows util-venv creation); `publish-2` has both markers. Most other fixtures include the markers so they show only the target's commands; container fixtures never have markers. New fixtures should do the same unless they test venv creation.
5. On failure, `test-actual/<name>.txt` is left in place. If the change is intentional, copy it to `test-expected/<name>.txt` in the same commit. Never commit `test-actual/`.
6. To add a test: fixture Makefile (+ markers as needed), `$(eval $(call TEST_RULE, <name>, <goal and vars>))` in the top-level Makefile, and `test-expected/<name>.txt`.
7. The top-level Makefile sets `OS := Unknown` and unexports `USE_DOCKER` / `USE_PODMAN` so output is platform-stable. Do not remove that.

Fixtures set `PYTHON_IMAGES := python:3.X python:3.Y`, but without `USE_DOCKER` / `USE_PODMAN` `Makefile.base` forces `PYTHON_IMAGES := system` (consumer settings included). Only the `*-use-docker` / `*-use-podman` fixtures show per-image output, so `test-exclude` does not actually exercise `PYTHON_IMAGES_EXCLUDE`. Changing the default image list in `Makefile.base` does not update snapshots; it still needs a README update when user-facing.

`commit-overrides` / `commit-overrides-unittest-parallel` / `publish-overrides` are the pass-through tests for make variables. New variables that appear in recipes should show up there.

## `Makefile.base`

- `DEFAULT_VENV_BUILD` / `DEFAULT_VENV_BIN` / `DEFAULT_VENV_PYTHON` / `DEFAULT_VENV_BIN_EX` are public consumer API (README, tool fixtures) in both makefiles; don't rename them or change their meaning.
- System Python by default (`PYTHON_IMAGES := system`). `USE_DOCKER=1` / `USE_PODMAN=1` switches to official `python:X.Y` images; `VENV_RUN_FN` wraps recipes in `docker run` / `podman run`.
- `VENV_RULE_FN` — one venv per image under `build/venv/<image-name>` with a `.build` marker.
- `VENV_COMMAND_FN` — per-image phony (e.g. `test-python-3-13`) plus aggregate (`test`). `IMAGE_NAME_FN` maps `python:3.13` → `python-3-13`.
- First image is the default: `cover`, `lint`, `doc`, and `publish` run only there; other images run tests only. A separate `-util` venv holds build, twine, and simple-git-changelog.
- `publish-<default-image>-util` depends on `commit` so parallel `make -j publish` cannot upload before tests finish. Do not drop that.
- Recipe bodies pass through `$(call)` / `$(eval)`: `$$` defers one expansion level, `$$$$` two. This is the easiest thing to break.
- Pre-include variables (`PYTHON_IMAGES`, `SPHINX_DOC`, `GHPAGES_SRC`, `UNITTEST_PARALLEL`, …) are read at include time. Changing when they are expanded can silently ignore consumer Makefiles.
- Pinned versions (`COVERAGE_VERSION`, `PYLINT_VERSION`, `SPHINX_VERSION`, `UNITTEST_PARALLEL_VERSION`) sit near the top of `Makefile.base`. Fixtures replace them with `X.Y.*` (or `bogus-*`), so bumping a pin changes no snapshot.
- Windows: `VENV_BIN` / `VENV_PYTHON` become `Scripts` / `python.exe` when not using containers. Tests force `OS := Unknown`, so do not delete the Windows branches as unused.

GNU Make (`makefile-gmake`). Must work on GNU Make 3.81 (the macOS default); guard 4.x-only features as output-sync is. Keep the MIT license header.

## `Makefile.tool`

Empty `test` / `lint` / `gh-pages`; `commit` = `test` + `lint`; venv at `build/env` from `TESTS_REQUIRE`. Tool fixtures extend `test`/`lint` like a consumer would. `PYTHON_IMAGE` (singular) is the container image, not `PYTHON_IMAGES`. The venv rule isn't a prerequisite of any built-in target; consumers (and tool fixtures) add `$(DEFAULT_VENV_BUILD)`. `Makefile.tool` duplicates the docker/podman run lines, pip defaults, Windows branch, and output-sync from `Makefile.base` — change both files together.

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
