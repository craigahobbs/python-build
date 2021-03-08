Python Build
============

**Python Build** is a lightweight `GNU Make <https://www.gnu.org/software/make/>`__-based build
system that encapsulates best practices for Python package development. Here are its features at a
glance:

- Run unit tests with multiple Python versions using the `official Docker Python images <https://hub.docker.com/_/python>`__
- Run unit tests with `coverage <https://pypi.org/project/coverage/>`__
- Perform static code analysis using `pylint <https://pypi.org/project/pylint/>`__
- Generate documentation using `Sphinx <https://pypi.org/project/Sphinx/>`__
- Publish documentation to `GitHub Pages <https://pages.github.com/>`__
- Publish the package to PyPI using `twine <https://pypi.org/project/twine/>`__


Project Setup
-------------

The basic structure of a Python Build project is as follows::

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

The basic Python Build ``Makefile`` is as follows. Note that it downloads ``Makefile.base`` and
``pylintrc`` files from Python Build. Python Build continually updates its development dependencies.

.. code-block:: make

   PYTHON_VERSIONS := \
       3.9 \
       3.8 \
       3.7

   # Sphinx documentation directory (optional)
   # SPHINX_DOC := doc

   # Download Python Build base makefile
   ifeq '$(wildcard Makefile.base)' ''
       $(info Downloading Makefile.base)
       $(shell curl -s -o Makefile.base 'https://raw.githubusercontent.com/craigahobbs/python-build/master/Makefile.base')
   endif

   # Download Python Build's pylintrc
   ifeq '$(wildcard pylintrc)' ''
       $(info Downloading pylintrc)
       $(shell curl -s -o pylintrc 'https://raw.githubusercontent.com/craigahobbs/python-build/master/pylintrc')
   endif

   # Include Python Build
   include Makefile.base

   clean:
       rm -rf Makefile.base pylintrc


Build Commands
--------------

Python Build exposes build commands as "phony" make targets. Make targets are executed as follows::

  make <target>

The following targets are available:

``commit``

   Execute the ``test``, ``lint``, ``doc``, and ``cover`` targets. This target should be run prior
   to any commit.

``test``

   Run the unit tests using the official Docker Python image for each Python version in
   ``PYTHON_VERSIONS``. Unit tests are run using Python's built-in `unittest
   <https://docs.python.org/3/library/unittest.html#command-line-interface>`__ command-line tool.

   You can run unit tests against a specific version of Python. For example, to run unit tests with
   Python "3.x", use the ``test-python-3-x`` target.

   To run a single unit test, use the ``TEST`` make variable::

     make test TEST=tests.test_module_name.TestCase.test_name

   To run all unit tests in a test file::

     make test TEST=tests.test_module_name

``lint``

   Run pylint on the ``setup.py`` file and all Python source code under the ``src`` directory.

``doc``

   Run sphinx-build on the Sphinx documentation directory (optional, defined by the ``SPHINX_DOC``
   make variable). The HTML documentation index is located at ``build/doc/html/index.html``.

``cover``

   Run unit tests with coverage. By default, "make cover" fails if coverage is less than 100%. The
   HTML coverage report index is located at ``build/coverage/index.html``.

   The ``TEST`` make variable is supported as described in the ``test`` target above.

``clean``

   Delete all development artifacts.

``superclean``

   Delete all development artifacts and downloaded docker images.

``gh-pages``

   Publish the Sphinx HTML documentation to GitHub Pages. It first executes the ``clean`` and
   ``doc`` targets to produce a clean documentation build. It then does a git clone (or pull) of
   your repository to the ``../<pagage-name>.gh-pages`` directory, checks out the ``gh-pages``
   branch, and rsync's from the ``build/doc/html/`` directory. Afterward, review the changes,
   commit, and push to publish.

``twine``

   Publish the package to PyPI using twine.


Make Options
------------

To view the commands of any make target without executing, use the "-n" make argument::

  make -n test

To run targets in parallel, use the "-j" make argument. This can significantly decrease the time of
the ``commit`` target.

::

  make -j commit

Python Build Options
--------------------

Python Build exposes several make variables that can be modified in your makefile following the base
makefile include. For example, to change minimum coverage level failure setting::

  COVERAGE_REPORT_ARGS := --fail-under 75

The following variables are supported:

``PIP_ARGS``

   The pip tool's global command line arguments. Default is "--no-cache-dir --disable-pip-version-check".

``PIP_INSTALL_ARGS``

   The pip install command's command line arguments. Default is "--progress-bar off".

``COVERAGE_VERSION``

   The `coverage <https://pypi.org/project/coverage>`__ package version.

``COVERAGE_REPORT_ARGS``

   The coverage tool's command line arguments. Default is "--fail-under 100".

``PYLINT_VERSION``

   The `pylint <https://pypi.org/project/pylint>`__ package version.

``PYLINT_ARGS``

   The pylint command line arguments. Default is "-j 0".

``SPHINX_VERSION``

   The `Sphinx <https://pypi.org/project/Sphinx>`__ package version.

``SPHINX_RTD_THEME_VERSION``

   The `sphinx-rtd-theme <https://pypi.org/project/sphinx-rtd-theme/>`__ package version.

``SPHINX_ARGS``

   The sphinx-build global command line arguments. Default is "-W -a".


Extending Python Build
----------------------

The Python Build ``help``, ``commit``, ``clean``, and ``superclean`` targets may be extended either
by adding target commands or adding a target dependency.

Here's an example of adding commands to the ``help`` target::

  help:
      @echo '            [my-command]'

Here's an example of adding a target dependency to the ``commit`` target::

  commit: other-stuff

  .PHONY: other-stuff
  other-stuff:
      # do stuff...
