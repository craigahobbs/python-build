# Python Build

**Python Build** is a lightweight GNU Make-based build system for best-practice Python package
development. Python Build performs the following functions:

- Run unit tests with all actively maintained Python versions using the [official Docker Python images](https://hub.docker.com/_/python)
- Run unit tests with [coverage](https://pypi.org/project/coverage/)
- Perform static code analysis using [pylint](https://pypi.org/project/pylint/)
- Generate documentation using [Sphinx](https://pypi.org/project/Sphinx/)
- Publish documentation to [GitHub Pages](https://pages.github.com/)
- Create and update a project changelog file using [simple-git-changelog](https://pypi.org/project/simple-git-changelog/)
- Publish the package to PyPI using [twine](https://pypi.org/project/twine/)


## Contents

- [Project Setup](#project-setup)
- [Make Targets](#make-targets)
- [Make Options](#make-options)
- [Make Variables](#make-variables)
- [Extending Python Build](#extending-python-build)
- [Make Tips & Tricks](#make-tips--tricks)


## Project Setup

The basic structure of a Python Build project is as follows:

```
|-- .gitignore
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

The basic Python Build "Makefile" is as follows:

``` make
# Download Python Build
define WGET
ifeq '$$(wildcard $(notdir $(1)))' ''
$$(info Downloading $(notdir $(1)))
_WGET := $$(shell $(call WGET_CMD, $(1)))
endif
endef
WGET_CMD = if which wget; then wget -q $(1); else curl -Os $(1); fi
$(eval $(call WGET, https://raw.githubusercontent.com/craigahobbs/python-build/main/Makefile.base))
$(eval $(call WGET, https://raw.githubusercontent.com/craigahobbs/python-build/main/pylintrc))

# Include Python Build
include Makefile.base

clean:
	rm -rf Makefile.base pylintrc
```

Note that the makefile automatically downloads "Makefile.base" and "pylintrc" files from Python
Build. Python Build continually updates its development dependencies to the latest stable versions.

Here is a typical Python Build project ".gitignore" file:

```
/.coverage
/Makefile.base
/build/
/dist/
/pylintrc
/src/*.egg-info/
__pycache__/
```

Notice that "Makefile.base" and "pylintrc" are ignored because they are downloaded by the Makefile.

Python package "setup.py" files can vary widely. Here's an
[example of a real-world setup.py](https://github.com/craigahobbs/schema-markdown/blob/main/setup.py)
that can serve as a starting place for your project's "setup.py".


## Make Targets

Python Build exposes build commands as "phony" make targets. For example, to run all pre-commit
targets, use the `commit` target:

```
make commit
```

The following targets are available:

### commit

Execute the [test](#test), [lint](#lint), [doc](#doc), and [cover](#cover) targets. This target
should be run prior to any commit.

### test

Run the unit tests using each Docker image in `PYTHON_IMAGES`. Unit tests are run using Python's
built-in
[unittest](https://docs.python.org/3/library/unittest.html#command-line-interface)
command-line tool.

You can run unit tests with a specific Docker image. For example, to run unit tests with the
"python:3.9" image, use the `test-python-3-9` target.

To run a single unit test, use the `TEST` make variable:

```
make test TEST=tests.test_module_name.TestCase.test_name
```

To run all unit tests in a test file:

```
make test TEST=tests.test_module_name
```

### lint

Run pylint on the "setup.py" file and all Python source code under the "src" directory.

### doc

Run sphinx-build on the Sphinx documentation directory (optional, defined by the `SPHINX_DOC` make
variable). The HTML documentation index is located at "build/doc/html/index.html".

### cover

Run unit tests with coverage. By default, "make cover" fails if coverage is less than 100%. The HTML
coverage report index is located at "build/coverage/index.html".

The `TEST` make variable is supported as described in the [test](#test) target above.

### clean

Delete all development artifacts.

### superclean

Delete all development artifacts and downloaded docker images.

### changelog

Create and update the project's changelog file.

### publish

Publish the package to PyPI using twine.

### gh-pages

Publish the project documentation (if any) to GitHub Pages. It first executes the `clean` and
`commit` targets to produce a clean build.

The repository is then git-cloned (or pulled) to the "../\<repository-name>.gh-pages" directory, the
"gh-pages" branch is checked-out, and the directories and files defined by the "GHPAGES_SRC" make
variable are rsync-ed there. Afterward, review the changes, commit, and push to publish.

To create a "gh-pages" branch, enter the following shell commands:

```
git checkout --orphan gh-pages
git reset --hard
git commit --allow-empty -m "initializing gh-pages branch"
git push origin gh-pages
```


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

Python Build exposes several make variables that can be modified in your makefile. For example, to
change minimum coverage level failure setting:

```
include Makefile.base

COVERAGE_REPORT_ARGS := $(COVERAGE_REPORT_ARGS) --fail-under 75
```

The following variables are supported:

- `PIP_ARGS` - The pip tool's global command line arguments. Default is "--no-cache-dir --disable-pip-version-check".

- `PIP_INSTALL_ARGS` - The pip install command's command line arguments. Default is "--progress-bar off".

- `COVERAGE_VERSION` - The [coverage](https://pypi.org/project/coverage) package version.

- `COVERAGE_ARGS` - The coverage tool's command line arguments. Default is "--branch".

- `COVERAGE_REPORT_ARGS` - The coverage report tool's command line arguments. Default is "--fail-under 100".

- `PYLINT_VERSION` - The [pylint](https://pypi.org/project/pylint) package version.

- `PYLINT_ARGS` - The pylint command line arguments. Default is "-j 0".

- `SPHINX_VERSION` - The [Sphinx](https://pypi.org/project/Sphinx) package version.

- `SPHINX_RTD_THEME_VERSION` - The [sphinx-rtd-theme](https://pypi.org/project/sphinx-rtd-theme/) package version.

- `SPHINX_ARGS` - The sphinx-build global command line arguments. Default is "-W -a".

- `TESTS_REQUIRE` - Additional Python packages to install for unit tests.

- `UNITTEST_ARGS` - The Python unittest discovery tool's command line arguments. Default is "-v".

- `UNITTEST_PARALLEL_VERSION` - The [unittest-parallel](https://pypi.org/project/unittest-parallel) package version.

- `UNITTEST_PARALLEL_ARGS` - The unittest-parallel tool's command line arguments. Default is "-v".

- `UNITTEST_PARALLEL_COVERAGE_ARGS` - The unittest-parallel tool's coverage-related command line arguments.
   Default is "--coverage-branch --coverage-fail-under 100".


### Pre-Include Make Variables

The following make variables must be defined prior to the inclusion of the base makefile. This is
because they modify the make targets that Python Build generates on include. For example, to set a
Sphinx documentation directory:

```
SPHINX_DOC := doc

include Makefile.base
```

The following pre-include make variables are exposed:

- `PYTHON_IMAGES` - The list of supported Python docker images. Default is all actively maintained
  Python versions.

- `PYTHON_IMAGES_EXCLUDE` - The list of Python images to exclude. Default is "".

- `SPHINX_DOC` - The Sphinx documentation directory. Default is "".

- `GHPAGES_SRC` - The gh-pages target's source directories and files. Directories must end with a
  slash ("/"). Default is "build/doc/html/" if SPHINX_DOC is defined, otherwise "".

- `UNITTEST_PARALLEL` - If set, use unittest-parallel for running unit tests. Default is "".


### Other Make Variables

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

```
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
