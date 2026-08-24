---
name: python-build
description: >
  Develop a downstream python-build package (Makefile includes Makefile.base or
  Makefile.tool). Use when running make test, lint, cover, or commit; adding
  tests; or changing that Makefile. Do not use when editing the python-build
  repository itself.
---

# python-build (downstream)

This skill is the build workflow for **packages that include** python-build. Package-specific behavior stays in the consumer `AGENTS.md`. Human reference for every target and variable is `README.md` in the same directory as this skill. Do not use this skill when changing `Makefile.base` / `Makefile.tool` themselves — that is python-build's `AGENTS.md`.

Load this file from `../python-build/SKILL.md` if that file exists, otherwise from [https://raw.githubusercontent.com/craigahobbs/python-build/main/SKILL.md](https://raw.githubusercontent.com/craigahobbs/python-build/main/SKILL.md). If neither is available, `make help` and the consumer `Makefile` are enough for day-to-day work; do not invent a second toolchain.

## Identify

The consumer `Makefile` downloads `Makefile.base` and `pylintrc` (or `Makefile.tool`) on first run, copies from `../python-build` when that tree exists, and `include`s the downloaded file. Those downloads are gitignored; `make clean` deletes them. Do not commit or hand-edit them. Do not rewrite the WGET stub.

Layout for `Makefile.base` packages: `src/<package>/`, tests at `src/tests/`, metadata in `pyproject.toml`. unittest discovery is `-t src/ -s src/tests/`.

## Commands (`Makefile.base`)

Run from the consumer repo root. `make` creates venvs under `build/venv/` and installs the package editable plus `TESTS_REQUIRE`. Venvs have no pip; extra test packages belong in `TESTS_REQUIRE`, not `pip install`.

| Target | Purpose |
| --- | --- |
| `make test` | unittest (`-W error`) on each `PYTHON_IMAGES` image |
| `make lint` | pylint on `src` (default image only) |
| `make cover` | branch coverage on the default image; **fails under 100%** unless the Makefile overrides `COVERAGE_REPORT_ARGS` |
| `make commit` | `test` + `lint` + `doc` + `cover` — the quality gate |
| `make clean` | `build/`, `dist/`, `.coverage`, egg-info, `__pycache__` (consumer stubs also remove the downloads) |
| `make superclean` | `clean` plus pulled container images |

One test or module (also works with `make cover`):

```
make test TEST=tests.test_module.TestClass.test_name
```

`TEST=` is passed to `python -m unittest`, not to discover. Use the `tests.` prefix. Do not use discover-relative ids such as `test_main.TestMain.test_foo`.

`make -n <target>` prints the commands without running them. `make -j commit` is supported.

Default `make` uses the system Python. Multi-version: `make commit USE_DOCKER=1` or `USE_PODMAN=1`. Cover, lint, doc, and publish run only on the first image in `PYTHON_IMAGES`; remaining images run tests only.

HTML coverage: `build/coverage/index.html`.

### Only when asked

- `make changelog` — rewrites `CHANGELOG.md` from git
- `make publish` — PyPI via twine (depends on `commit`)
- `make gh-pages` — rsync `GHPAGES_SRC` to `../<repo>.gh-pages`

Version for packages is `[project].version` in `pyproject.toml`. Bump it only as part of a release.

## Local overrides

After this skill, read the consumer `Makefile` and `AGENTS.md`. Common knobs (full catalog in the README):

- `TESTS_REQUIRE` — extra pip specs for tests
- `PYLINT_ARGS` — appended pylint flags (often disables missing-docstring)
- `SPHINX_DOC` — unset means `make doc` is a no-op; `make commit` still depends on `doc`
- `UNITTEST_PARALLEL` — use unittest-parallel instead of unittest discover
- `PYTHON_IMAGES` / `PYTHON_IMAGES_EXTRA` / `PYTHON_IMAGES_EXCLUDE` — must be set **before** `include Makefile.base`

Do not lower the coverage gate, skip `cover`, or leave untested branches. `# pragma: no cover` only for version/platform-dependent code the consumer already uses that way.

## Do not

- Add pytest, tox, ruff, black, mypy, or another task runner
- Call pip inside the venv or hard-code `build/venv/.../bin` vs `Scripts`
- Add Sphinx, CI configs, or Makefile-stub rewrites unless asked
- Treat downloaded `Makefile.base` / `pylintrc` / `Makefile.tool` as project source

## `Makefile.tool`

Non-package repos: empty `test` / `lint` / `gh-pages`, `commit` = `test` + `lint`, venv at `build/env` from `TESTS_REQUIRE` (required). Extend those targets; use `$(DEFAULT_VENV_BUILD)` as a prerequisite and `$(DEFAULT_VENV_BIN)` / `$(DEFAULT_VENV_PYTHON)` to run tools. No `cover`, `changelog`, or `publish` unless the consumer Makefile adds them.
