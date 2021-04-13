# Python Build

## Contents

- [Introduction](#introduction)
- [Project Setup](#project-setup)
- [Make Targets](#make-targets)
- [Make Options](#make-options)
- [Make Variables](#make-variables)
- [Extending Python Build](#extending-python-build)
- [Make Tips & Tricks](#make-tips--tricks)


## Introduction

**Python Build** is a lightweight GNU Make-based build system for best-practice Python package
development. Python Build performs the following functions:

- Run unit tests with multiple Python versions using the [official Docker Python images](https://hub.docker.com/_/python)
- Run unit tests with [coverage](https://pypi.org/project/coverage/)
- Perform static code analysis using [pylint](https://pypi.org/project/pylint/)
- Generate documentation using [Sphinx](https://pypi.org/project/Sphinx/)
- Publish documentation to [GitHub Pages](https://pages.github.com/)
- Publish the package to PyPI using [twine](https://pypi.org/project/twine/)


## Project Setup

The basic structure of a Python Build project is as follows:

``` make
|-- Makefile
|-- README.rst
|-- setup.py
`-- src
    |-- __init__.py
    |-- module_name
    |   |-- __init__.py
    |   `-- module_name.py
    `-- tests
        |-- __init__.py
        `-- test_module_name.py
```

The basic Python Build `Makefile` is as follows:

``` make
PYTHON_VERSIONS := \
    3.9 \
    3.8 \
    3.7

# Sphinx documentation directory (optional)
# SPHINX_DOC := doc

# Download Python Build base makefile and pylintrc
define WGET
ifeq '$$(wildcard $(notdir $(1)))' ''
$$(info Downloading $(notdir $(1)))
_WGET := $$(shell if which wget; then wget -q $(1); else curl -Os $(1); fi)
endif
endef
$(eval $(call WGET, https://raw.githubusercontent.com/craigahobbs/python-build/main/Makefile.base))
$(eval $(call WGET, https://raw.githubusercontent.com/craigahobbs/python-build/main/pylintrc))

# Include Python Build
include Makefile.base

clean:
	rm -rf Makefile.base pylintrc
```

Note that the makefile automatically downloads `Makefile.base` and `pylintrc` files from Python
Build. Python Build continually updates its development dependencies to the latest stable versions.


## Make Targets

Python Build exposes build commands as "phony" make targets. Make targets are executed as follows:

```
make <target>
```

The following targets are available:

### commit

Execute the [test](#test), [lint](#lint), [doc](#doc), and [cover](#cover) targets. This target
should be run prior to any commit.

### test

Run the unit tests using the official Docker Python image for each Python version in
`PYTHON_VERSIONS`. Unit tests are run using Python's built-in
[unittest](https://docs.python.org/3/library/unittest.html#command-line-interface) command-line
tool.

You can run unit tests against a specific version of Python. For example, to run unit tests with
Python "3.x", use the `test-python-3-x` target.

To run a single unit test, use the `TEST` make variable:

```
make test TEST=tests.test_module_name.TestCase.test_name
```

To run all unit tests in a test file:

```
make test TEST=tests.test_module_name
```

### lint

Run pylint on the `setup.py` file and all Python source code under the `src` directory.

### doc

Run sphinx-build on the Sphinx documentation directory (optional, defined by the `SPHINX_DOC` make
variable). The HTML documentation index is located at `build/doc/html/index.html`.

### cover

Run unit tests with coverage. By default, "make cover" fails if coverage is less than 100%. The HTML
coverage report index is located at `build/coverage/index.html`.

The `TEST` make variable is supported as described in the [test](#test) target above.

### clean

Delete all development artifacts.

### superclean

Delete all development artifacts and downloaded docker images.

### gh-pages

Publish the Sphinx HTML documentation to GitHub Pages. It first executes the `clean` and `doc`
targets to produce a clean documentation build. It then does a git clone (or pull) of your
repository to the `../<pagage-name>.gh-pages` directory, checks out the `gh-pages` branch, and
rsync's from the `build/doc/html/` directory. Afterward, review the changes, commit, and push to
publish.

To create a `gh-pages` branch, enter the following shell commands:

```
git checkout --orphan gh-pages
git reset --hard
git commit --allow-empty -m "initializing gh-pages branch"
git push origin gh-pages
```

### publish

Publish the package to PyPI using twine.


## Make Options

To view the commands of any make target without executing, use the "-n" make argument:

```
make -n test
```

To run targets in parallel, use the "-j" make argument. This can significantly decrease the time of
the [commit](#commit) target.

```
make -j commit
```


## Make Variables

Python Build exposes several make variables that can be modified in your makefile following the base
makefile include. For example, to change minimum coverage level failure setting:

```
COVERAGE_REPORT_ARGS := --fail-under 75
```

The following variables are supported:

- `PIP_ARGS` - The pip tool's global command line arguments. Default is "--no-cache-dir --disable-pip-version-check".

- `PIP_INSTALL_ARGS` - The pip install command's command line arguments. Default is "--progress-bar off".

- `COVERAGE_VERSION` - The [coverage](https://pypi.org/project/coverage) package version.

- `COVERAGE_REPORT_ARGS` - The coverage tool's command line arguments. Default is "--fail-under 100".

- `PYLINT_VERSION` - The [pylint](https://pypi.org/project/pylint) package version.

- `PYLINT_ARGS` - The pylint command line arguments. Default is "-j 0".

- `SPHINX_VERSION` - The [Sphinx](https://pypi.org/project/Sphinx) package version.

- `SPHINX_RTD_THEME_VERSION` - The [sphinx-rtd-theme](https://pypi.org/project/sphinx-rtd-theme/) package version.

- `SPHINX_ARGS` - The sphinx-build global command line arguments. Default is "-W -a".

- `TESTS_REQUIRE` - Additional Python packages to install for unit tests.

- `DUMP_RULES` - Dump generated make rules. This is intended to be used from the command line:

```
make DUMP_RULES=1
```

- `NO_DOCKER` - Use the system python instead of docker. This is intended to be used from the command line:

```
make commit NO_DOCKER=1
```


## Extending Python Build

All of the Python Build [targets](#make-targets) may be extended either by adding additional
commands or adding a target dependency. Add additional commands to execute when a target (and all
its dependencies) is complete:

```
commit:
	@echo 'Build succeeded!'
```

Add a target dependency when you want the new dependency to execute in parallel (for [parallel
builds](#make-options)):

```
.PHONY: other-stuff
other-stuff:
    # do stuff...

commit: other-stuff
```


## Make Tips & Tricks

### Embed Python in a makefile

Python can be embedded in a makefile by first defining the Python script, exporting the Python
script, and executing the Python script with the "-c" argument. Make variables can even be
incorporated into the Python script. Here's an example:

``` make
TITLE := Hello, World!

define PYTHON_SCRIPT
print('$(TITLE)')
for x in range(10):
    print(f'x = {x}')
endef

export PYTHON_SCRIPT

.PHONY: python-script
python-script:
	python3 -c "$$PYTHON_SCRIPT"
```

Running make yields the following output:

```
Hello, World!
x = 0
x = 1
x = 2
x = 3
x = 4
x = 5
x = 6
x = 7
x = 8
x = 9
```
