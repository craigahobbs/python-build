# python-build

**python-build** is a lightweight GNU Make-based build system for best-practice Python package
development.

- Uses the system Python or the official Python images using [podman](https://podman.io/)
- Run unit tests with [unittest](https://docs.python.org/3/library/unittest.html)
  - Optionally run tests with [unittest-parallel](https://pypi.org/project/unittest-parallel/)
- Code coverage using [coverage](https://pypi.org/project/coverage/)
  - 100% code coverage enforced (configurable)
- Static code analysis using [pylint](https://pypi.org/project/pylint/)
- Package documentation using [Sphinx](https://pypi.org/project/Sphinx/)
- Publish the package to [PyPI](https://pypi.org/)
- Publish documentation to [GitHub Pages](https://pages.github.com/)


## Contents

- [Project Setup](#project-setup)
- [Make Targets](#make-targets)
- [Make Options](#make-options)
- [Make Variables](#make-variables)
- [Extending python-build](#extending-python-build)
- [Make Tips and Tricks](#make-tips-and-tricks)


## Project Setup

The basic structure of a python-build project is as follows:

~~~
|-- .gitignore
|-- Makefile
|-- README.rst
|-- pyproject.toml
|-- setup.cfg
`-- src
    |-- __init__.py
    |-- module_name
    |   |-- __init__.py
    |   `-- module_name.py
    `-- tests
        |-- __init__.py
        `-- test_module_name.py
~~~

The basic python-build "Makefile" is as follows:

~~~ make
# Download python-build
PYTHON_BUILD_DIR ?= ../python-build
define WGET
ifeq '$$(wildcard $(notdir $(1)))' ''
$$(info Downloading $(notdir $(1)))
$$(shell [ -f $(PYTHON_BUILD_DIR)/$(notdir $(1)) ] && cp $(PYTHON_BUILD_DIR)/$(notdir $(1)) . || $(call WGET_CMD, $(1)))
endif
endef
WGET_CMD = if command -v wget >/dev/null 2>&1; then wget -q -c $(1); else curl -f -Os $(1); fi
$(eval $(call WGET, https://craigahobbs.github.io/python-build/Makefile.base))
$(eval $(call WGET, https://craigahobbs.github.io/python-build/pylintrc))

# Include python-build
include Makefile.base

clean:
	rm -rf Makefile.base pylintrc
~~~

Note that the makefile automatically downloads "Makefile.base" and "pylintrc" files from python-build.
It continually updates its development dependencies to the latest stable versions.

Here is a typical python-build project ".gitignore" file:

~~~
/.coverage
/Makefile.base
/build/
/dist/
/pylintrc
/src/*.egg-info/
__pycache__/
~~~

Notice that "Makefile.base" and "pylintrc" are ignored because they are downloaded by the Makefile.


## Make Targets

python-build exposes build commands as "phony" make targets. For example, to run all pre-commit
targets, use the `commit` target:

~~~
make commit
~~~

The following targets are available:

### commit

Execute the [test](#test), [lint](#lint), [doc](#doc), and [cover](#cover) targets. This target
should be run prior to any commit.

### test

Run the unit tests using each image in `PYTHON_IMAGES`. Unit tests are run using Python's
built-in
[unittest](https://docs.python.org/3/library/unittest.html#command-line-interface)
command-line tool.

You can run unit tests with a specific image. For example, to run unit tests with the
"python:3.X" image, use the `test-python-3-X` target.

To run a single unit test, use the `TEST` make variable:

~~~
make test TEST=tests.test_module_name.TestCase.test_name
~~~

To run all unit tests in a test file:

~~~
make test TEST=tests.test_module_name
~~~

### lint

Run pylint on all Python source code under the "src" directory.

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

Delete all development artifacts and downloaded images.

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

~~~
git checkout --orphan gh-pages
git reset --hard
git commit --allow-empty -m "initializing gh-pages branch"
git push origin gh-pages
~~~


## Make Options

To view the commands of any make target without executing, use the "-n" make argument:

~~~
make -n test
~~~

To run targets in parallel, use the "-j" make argument. This can significantly decrease the time of
the [commit](#commit) target.

~~~
make -j commit
~~~


## Make Variables

python-build exposes several make variables that can be modified in your makefile. For example, to
change minimum coverage level failure setting:

~~~ make
include Makefile.base

COVERAGE_REPORT_ARGS := $(COVERAGE_REPORT_ARGS) --fail-under 75
~~~

The following variables are supported:

- `PIP_ARGS` - The pip tool's global command line arguments. Default is "--no-cache-dir --disable-pip-version-check".

- `PIP_INSTALL_ARGS` - The pip install command's command line arguments. Default is "--progress-bar off".

- `COVERAGE_VERSION` - The [coverage](https://pypi.org/project/coverage) package version.

- `COVERAGE_ARGS` - The coverage tool's command line arguments. Default is "--branch".

- `COVERAGE_REPORT_ARGS` - The coverage report tool's command line arguments. Default is "--fail-under 100".

- `PYLINT_VERSION` - The [pylint](https://pypi.org/project/pylint) package version.

- `PYLINT_ARGS` - The pylint command line arguments. Default is "-j 0".

- `SPHINX_VERSION` - The [Sphinx](https://pypi.org/project/Sphinx) package version.

- `SPHINX_ARGS` - The sphinx-build global command line arguments. Default is "-W -a".

- `TESTS_REQUIRE` - Additional Python packages to install for unit tests.

- `UNITTEST_ARGS` - The Python unittest discovery tool's command line arguments. Default is "-v".

- `UNITTEST_PARALLEL_VERSION` - The [unittest-parallel](https://pypi.org/project/unittest-parallel) package version.

- `UNITTEST_PARALLEL_ARGS` - The unittest-parallel tool's command line arguments. Default is "-v".

- `UNITTEST_PARALLEL_COVERAGE_ARGS` - The unittest-parallel tool's coverage-related command line arguments.
   Default is "--coverage-branch --coverage-fail-under 100".

- `GHPAGES_RSYNC_ARGS` - Additional rsync arguments for the `gh-pages` target.


### Pre-Include Make Variables

The following make variables must be defined prior to the inclusion of the base makefile. This is
because they modify the make targets that python-build generates on include. For example, to set a
Sphinx documentation directory:

~~~ make
SPHINX_DOC := doc

include Makefile.base
~~~

The following pre-include make variables are exposed:

- `PYTHON_IMAGES` - The list of supported Python images. Default is all actively maintained
  Python versions.

- `PYTHON_IMAGES_EXCLUDE` - The list of Python images to exclude. Default is "".

- `PYTHON_IMAGES_EXTRA` - The list of extra Python images. Default is "".

- `SPHINX_DOC` - The Sphinx documentation directory. Default is "".

- `GHPAGES_SRC` - The gh-pages target's source directories and files. Directories must end with a
  slash ("/"). Default is "build/doc/html/" if SPHINX_DOC is defined, otherwise "".

- `UNITTEST_PARALLEL` - If set, use unittest-parallel for running unit tests. Default is "".


### Other Make Variables

- `USE_PODMAN` - Use [podman](https://podman.io/) and test with the official Python images.

~~~
make commit USE_PODMAN=1
~~~


## Extending python-build

All of the python-build [targets](#make-targets) may be extended either by adding additional
commands or adding a target dependency. Add additional commands to execute when a target (and all
its dependencies) is complete:

~~~ make
commit:
	@echo 'Build succeeded!'
~~~

Add a target dependency when you want the new dependency to execute in parallel (for [parallel
builds](#make-options)):

~~~ make
.PHONY: other-stuff
other-stuff:
    # do stuff...

commit: other-stuff
~~~


## Make Tips and Tricks

### Embed Python in a Makefile

Python can be embedded in a makefile by first defining the Python script, exporting the Python
script, and executing the Python script with the "-c" argument. Make variables can even be
incorporated into the Python script. Here's an example:

~~~ make
TITLE := Hello, World!
COUNT := 3

define PYTHON_SCRIPT
print('$(TITLE)')
for x in range(1, $(COUNT) + 1):
    print(f'x = {x}')
endef
export PYTHON_SCRIPT

.PHONY: python-script
python-script:
	python3 -c "$$PYTHON_SCRIPT"
~~~

Running make yields the following output:

~~~
Hello, World!
x = 1
x = 2
x = 3
~~~
