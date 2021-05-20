# Licensed under the MIT License
# https://github.com/craigahobbs/python-build/blob/main/LICENSE

"""
Python Build makefile unit tests
"""

# pylint: disable=line-too-long, missing-function-docstring

from contextlib import contextmanager
import os
from pathlib import Path
import re
import subprocess
from tempfile import TemporaryDirectory
import unittest


# Read the base makefile
with open('Makefile.base', 'r') as file_makefile_base:
    MAKEFILE_BASE = file_makefile_base.read()


# Helper context manager to create a list of files in a temporary directory
@contextmanager
def create_test_files(file_defs):
    tempdir = TemporaryDirectory() # pylint: disable=consider-using-with
    try:
        for path_parts, content in file_defs:
            if isinstance(path_parts, str):
                path_parts = [path_parts]
            path = os.path.join(tempdir.name, *path_parts)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'w', encoding='utf-8') as file_:
                file_.write(content)
        yield tempdir.name
    finally:
        tempdir.cleanup()


class PythonBuildTest(unittest.TestCase):
    """
    Python Build makefile unit tests
    """

    def assert_make_output(self, actual, expected):
        actual_clean = actual

        # Cleanup pip versions
        actual_clean = re.sub(r'=="\d+\..*?"', '=="X.X.X"', actual_clean, flags=re.MULTILINE)

        # Cleanup make message for macOS
        actual_clean = re.sub(r'^(make: Nothing to be done for )`', r"\1'", actual_clean, flags=re.MULTILINE)

        # Cleanup leading tabs for macOS
        actual_clean = re.sub(r'^\t\t', r'\t', actual_clean, flags=re.MULTILINE)

        self.assertEqual(actual_clean, expected)

    def test_help(self):
        test_files = create_test_files([
            ('Makefile', 'include Makefile.base'),
            ('Makefile.base', MAKEFILE_BASE)
        ])
        with test_files as test_dir:
            self.assert_make_output(
                subprocess.check_output(['make', '-n'], env={}, cwd=test_dir, stderr=subprocess.STDOUT, encoding='utf-8'),
                '''\
echo 'usage: make [changelog|clean|commit|cover|doc|gh-pages|lint|publish|superclean|test]'
'''
            )
            self.assert_make_output(
                subprocess.check_output(['make', 'help', '-n'], env={}, cwd=test_dir, stderr=subprocess.STDOUT, encoding='utf-8'),
                '''\
echo 'usage: make [changelog|clean|commit|cover|doc|gh-pages|lint|publish|superclean|test]'
'''
            )

    def test_help_dump_rules(self):
        test_files = create_test_files([
            ('Makefile', 'include Makefile.base'),
            ('Makefile.base', MAKEFILE_BASE)
        ])
        with test_files as test_dir:
            self.assert_make_output(
                subprocess.check_output(['make', 'DUMP_RULES=1', '-n'], env={}, cwd=test_dir, stderr=subprocess.STDOUT, encoding='utf-8'),
                '''\
TEST_PYTHON_3_9_VENV_DIR := build/venv/test-python-3-9
TEST_PYTHON_3_9_VENV_RUN := $(if $(NO_DOCKER),,docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.9)
TEST_PYTHON_3_9_VENV_CMD := $(TEST_PYTHON_3_9_VENV_RUN) $(TEST_PYTHON_3_9_VENV_DIR)/bin
TEST_PYTHON_3_9_VENV_BUILD := build/venv/test-python-3-9.build

$(TEST_PYTHON_3_9_VENV_BUILD):
ifeq '$(NO_DOCKER)' ''
\tif [ "$$(docker images -q python:3.9)" = "" ]; then docker pull -q python:3.9; fi
endif
\t$(TEST_PYTHON_3_9_VENV_RUN) python3 -m venv $(TEST_PYTHON_3_9_VENV_DIR)
\t$(TEST_PYTHON_3_9_VENV_CMD)/pip -q $(PIP_ARGS) install $(PIP_INSTALL_ARGS) --upgrade pip setuptools wheel
\t$(TEST_PYTHON_3_9_VENV_CMD)/pip $(PIP_ARGS) install $(PIP_INSTALL_ARGS) $(strip  -e . $(TESTS_REQUIRE))
\ttouch $@

.PHONY: test-python-3-9
test-python-3-9: $(TEST_PYTHON_3_9_VENV_BUILD)
\t$(TEST_PYTHON_3_9_VENV_CMD)/python3 -m unittest $(if $(TEST),-v $(TEST),discover -v -t src -s src/tests)$(if $(TEST_ARGS), $(TEST_ARGS))

.PHONY: test
test: test-python-3-9

TEST_PYTHON_3_10_RC_VENV_DIR := build/venv/test-python-3-10-rc
TEST_PYTHON_3_10_RC_VENV_RUN := $(if $(NO_DOCKER),,docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.10-rc)
TEST_PYTHON_3_10_RC_VENV_CMD := $(TEST_PYTHON_3_10_RC_VENV_RUN) $(TEST_PYTHON_3_10_RC_VENV_DIR)/bin
TEST_PYTHON_3_10_RC_VENV_BUILD := build/venv/test-python-3-10-rc.build

$(TEST_PYTHON_3_10_RC_VENV_BUILD):
ifeq '$(NO_DOCKER)' ''
\tif [ "$$(docker images -q python:3.10-rc)" = "" ]; then docker pull -q python:3.10-rc; fi
endif
\t$(TEST_PYTHON_3_10_RC_VENV_RUN) python3 -m venv $(TEST_PYTHON_3_10_RC_VENV_DIR)
\t$(TEST_PYTHON_3_10_RC_VENV_CMD)/pip -q $(PIP_ARGS) install $(PIP_INSTALL_ARGS) --upgrade pip setuptools wheel
\t$(TEST_PYTHON_3_10_RC_VENV_CMD)/pip $(PIP_ARGS) install $(PIP_INSTALL_ARGS) $(strip  -e . $(TESTS_REQUIRE))
\ttouch $@

.PHONY: test-python-3-10-rc
test-python-3-10-rc: $(TEST_PYTHON_3_10_RC_VENV_BUILD)
\t$(TEST_PYTHON_3_10_RC_VENV_CMD)/python3 -m unittest $(if $(TEST),-v $(TEST),discover -v -t src -s src/tests)$(if $(TEST_ARGS), $(TEST_ARGS))

.PHONY: test
test: test-python-3-10-rc

TEST_PYTHON_3_8_VENV_DIR := build/venv/test-python-3-8
TEST_PYTHON_3_8_VENV_RUN := $(if $(NO_DOCKER),,docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.8)
TEST_PYTHON_3_8_VENV_CMD := $(TEST_PYTHON_3_8_VENV_RUN) $(TEST_PYTHON_3_8_VENV_DIR)/bin
TEST_PYTHON_3_8_VENV_BUILD := build/venv/test-python-3-8.build

$(TEST_PYTHON_3_8_VENV_BUILD):
ifeq '$(NO_DOCKER)' ''
\tif [ "$$(docker images -q python:3.8)" = "" ]; then docker pull -q python:3.8; fi
endif
\t$(TEST_PYTHON_3_8_VENV_RUN) python3 -m venv $(TEST_PYTHON_3_8_VENV_DIR)
\t$(TEST_PYTHON_3_8_VENV_CMD)/pip -q $(PIP_ARGS) install $(PIP_INSTALL_ARGS) --upgrade pip setuptools wheel
\t$(TEST_PYTHON_3_8_VENV_CMD)/pip $(PIP_ARGS) install $(PIP_INSTALL_ARGS) $(strip  -e . $(TESTS_REQUIRE))
\ttouch $@

.PHONY: test-python-3-8
test-python-3-8: $(TEST_PYTHON_3_8_VENV_BUILD)
\t$(TEST_PYTHON_3_8_VENV_CMD)/python3 -m unittest $(if $(TEST),-v $(TEST),discover -v -t src -s src/tests)$(if $(TEST_ARGS), $(TEST_ARGS))

.PHONY: test
test: test-python-3-8

TEST_PYTHON_3_7_VENV_DIR := build/venv/test-python-3-7
TEST_PYTHON_3_7_VENV_RUN := $(if $(NO_DOCKER),,docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.7)
TEST_PYTHON_3_7_VENV_CMD := $(TEST_PYTHON_3_7_VENV_RUN) $(TEST_PYTHON_3_7_VENV_DIR)/bin
TEST_PYTHON_3_7_VENV_BUILD := build/venv/test-python-3-7.build

$(TEST_PYTHON_3_7_VENV_BUILD):
ifeq '$(NO_DOCKER)' ''
\tif [ "$$(docker images -q python:3.7)" = "" ]; then docker pull -q python:3.7; fi
endif
\t$(TEST_PYTHON_3_7_VENV_RUN) python3 -m venv $(TEST_PYTHON_3_7_VENV_DIR)
\t$(TEST_PYTHON_3_7_VENV_CMD)/pip -q $(PIP_ARGS) install $(PIP_INSTALL_ARGS) --upgrade pip setuptools wheel
\t$(TEST_PYTHON_3_7_VENV_CMD)/pip $(PIP_ARGS) install $(PIP_INSTALL_ARGS) $(strip  -e . $(TESTS_REQUIRE))
\ttouch $@

.PHONY: test-python-3-7
test-python-3-7: $(TEST_PYTHON_3_7_VENV_BUILD)
\t$(TEST_PYTHON_3_7_VENV_CMD)/python3 -m unittest $(if $(TEST),-v $(TEST),discover -v -t src -s src/tests)$(if $(TEST_ARGS), $(TEST_ARGS))

.PHONY: test
test: test-python-3-7

TEST_PYTHON_3_6_VENV_DIR := build/venv/test-python-3-6
TEST_PYTHON_3_6_VENV_RUN := $(if $(NO_DOCKER),,docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.6)
TEST_PYTHON_3_6_VENV_CMD := $(TEST_PYTHON_3_6_VENV_RUN) $(TEST_PYTHON_3_6_VENV_DIR)/bin
TEST_PYTHON_3_6_VENV_BUILD := build/venv/test-python-3-6.build

$(TEST_PYTHON_3_6_VENV_BUILD):
ifeq '$(NO_DOCKER)' ''
\tif [ "$$(docker images -q python:3.6)" = "" ]; then docker pull -q python:3.6; fi
endif
\t$(TEST_PYTHON_3_6_VENV_RUN) python3 -m venv $(TEST_PYTHON_3_6_VENV_DIR)
\t$(TEST_PYTHON_3_6_VENV_CMD)/pip -q $(PIP_ARGS) install $(PIP_INSTALL_ARGS) --upgrade pip setuptools wheel
\t$(TEST_PYTHON_3_6_VENV_CMD)/pip $(PIP_ARGS) install $(PIP_INSTALL_ARGS) $(strip  -e . $(TESTS_REQUIRE))
\ttouch $@

.PHONY: test-python-3-6
test-python-3-6: $(TEST_PYTHON_3_6_VENV_BUILD)
\t$(TEST_PYTHON_3_6_VENV_CMD)/python3 -m unittest $(if $(TEST),-v $(TEST),discover -v -t src -s src/tests)$(if $(TEST_ARGS), $(TEST_ARGS))

.PHONY: test
test: test-python-3-6

COVER_PYTHON_3_9_VENV_DIR := build/venv/cover-python-3-9
COVER_PYTHON_3_9_VENV_RUN := $(if $(NO_DOCKER),,docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.9)
COVER_PYTHON_3_9_VENV_CMD := $(COVER_PYTHON_3_9_VENV_RUN) $(COVER_PYTHON_3_9_VENV_DIR)/bin
COVER_PYTHON_3_9_VENV_BUILD := build/venv/cover-python-3-9.build

$(COVER_PYTHON_3_9_VENV_BUILD):
ifeq '$(NO_DOCKER)' ''
\tif [ "$$(docker images -q python:3.9)" = "" ]; then docker pull -q python:3.9; fi
endif
\t$(COVER_PYTHON_3_9_VENV_RUN) python3 -m venv $(COVER_PYTHON_3_9_VENV_DIR)
\t$(COVER_PYTHON_3_9_VENV_CMD)/pip -q $(PIP_ARGS) install $(PIP_INSTALL_ARGS) --upgrade pip setuptools wheel
\t$(COVER_PYTHON_3_9_VENV_CMD)/pip $(PIP_ARGS) install $(PIP_INSTALL_ARGS) $(strip  -e . coverage=="$(COVERAGE_VERSION)" $(TESTS_REQUIRE))
\ttouch $@

.PHONY: cover-python-3-9
cover-python-3-9: $(COVER_PYTHON_3_9_VENV_BUILD)
\t$(COVER_PYTHON_3_9_VENV_CMD)/python3 -m coverage run --branch --source src -m unittest $(if $(TEST),-v $(TEST),discover -v -t src -s src/tests)$(if $(TEST_ARGS), $(TEST_ARGS))
\t$(COVER_PYTHON_3_9_VENV_CMD)/python3 -m coverage html -d build/coverage
\t$(COVER_PYTHON_3_9_VENV_CMD)/python3 -m coverage report $(COVERAGE_REPORT_ARGS)

.PHONY: cover
cover: cover-python-3-9

LINT_PYTHON_3_9_VENV_DIR := build/venv/lint-python-3-9
LINT_PYTHON_3_9_VENV_RUN := $(if $(NO_DOCKER),,docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.9)
LINT_PYTHON_3_9_VENV_CMD := $(LINT_PYTHON_3_9_VENV_RUN) $(LINT_PYTHON_3_9_VENV_DIR)/bin
LINT_PYTHON_3_9_VENV_BUILD := build/venv/lint-python-3-9.build

$(LINT_PYTHON_3_9_VENV_BUILD):
ifeq '$(NO_DOCKER)' ''
\tif [ "$$(docker images -q python:3.9)" = "" ]; then docker pull -q python:3.9; fi
endif
\t$(LINT_PYTHON_3_9_VENV_RUN) python3 -m venv $(LINT_PYTHON_3_9_VENV_DIR)
\t$(LINT_PYTHON_3_9_VENV_CMD)/pip -q $(PIP_ARGS) install $(PIP_INSTALL_ARGS) --upgrade pip setuptools wheel
\t$(LINT_PYTHON_3_9_VENV_CMD)/pip $(PIP_ARGS) install $(PIP_INSTALL_ARGS) $(strip  -e . pylint=="$(PYLINT_VERSION)")
\ttouch $@

.PHONY: lint-python-3-9
lint-python-3-9: $(LINT_PYTHON_3_9_VENV_BUILD)
\t$(LINT_PYTHON_3_9_VENV_CMD)/python3 -m pylint $(PYLINT_ARGS) setup.py src

.PHONY: lint
lint: lint-python-3-9

PUBLISH_PYTHON_3_9_VENV_DIR := build/venv/publish-python-3-9
PUBLISH_PYTHON_3_9_VENV_RUN := $(if $(NO_DOCKER),,docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.9)
PUBLISH_PYTHON_3_9_VENV_CMD := $(PUBLISH_PYTHON_3_9_VENV_RUN) $(PUBLISH_PYTHON_3_9_VENV_DIR)/bin
PUBLISH_PYTHON_3_9_VENV_BUILD := build/venv/publish-python-3-9.build

$(PUBLISH_PYTHON_3_9_VENV_BUILD):
ifeq '$(NO_DOCKER)' ''
\tif [ "$$(docker images -q python:3.9)" = "" ]; then docker pull -q python:3.9; fi
endif
\t$(PUBLISH_PYTHON_3_9_VENV_RUN) python3 -m venv $(PUBLISH_PYTHON_3_9_VENV_DIR)
\t$(PUBLISH_PYTHON_3_9_VENV_CMD)/pip -q $(PIP_ARGS) install $(PIP_INSTALL_ARGS) --upgrade pip setuptools wheel
\t$(PUBLISH_PYTHON_3_9_VENV_CMD)/pip $(PIP_ARGS) install $(PIP_INSTALL_ARGS) $(strip  twine)
\ttouch $@

.PHONY: publish-python-3-9
publish-python-3-9: $(PUBLISH_PYTHON_3_9_VENV_BUILD)
\t$(PUBLISH_PYTHON_3_9_VENV_CMD)/python3 setup.py sdist
\t$(PUBLISH_PYTHON_3_9_VENV_CMD)/twine check dist/*.tar.gz
\t$(PUBLISH_PYTHON_3_9_VENV_CMD)/twine upload dist/*.tar.gz

.PHONY: publish
publish: publish-python-3-9

CHANGELOG_PYTHON_3_9_VENV_DIR := build/venv/changelog-python-3-9
CHANGELOG_PYTHON_3_9_VENV_RUN := $(if $(NO_DOCKER),,docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.9)
CHANGELOG_PYTHON_3_9_VENV_CMD := $(CHANGELOG_PYTHON_3_9_VENV_RUN) $(CHANGELOG_PYTHON_3_9_VENV_DIR)/bin
CHANGELOG_PYTHON_3_9_VENV_BUILD := build/venv/changelog-python-3-9.build

$(CHANGELOG_PYTHON_3_9_VENV_BUILD):
ifeq '$(NO_DOCKER)' ''
\tif [ "$$(docker images -q python:3.9)" = "" ]; then docker pull -q python:3.9; fi
endif
\t$(CHANGELOG_PYTHON_3_9_VENV_RUN) python3 -m venv $(CHANGELOG_PYTHON_3_9_VENV_DIR)
\t$(CHANGELOG_PYTHON_3_9_VENV_CMD)/pip -q $(PIP_ARGS) install $(PIP_INSTALL_ARGS) --upgrade pip setuptools wheel
\t$(CHANGELOG_PYTHON_3_9_VENV_CMD)/pip $(PIP_ARGS) install $(PIP_INSTALL_ARGS) $(strip  simple-git-changelog)
\ttouch $@

.PHONY: changelog-python-3-9
changelog-python-3-9: $(CHANGELOG_PYTHON_3_9_VENV_BUILD)
\t$(CHANGELOG_PYTHON_3_9_VENV_CMD)/simple-git-changelog

.PHONY: changelog
changelog: changelog-python-3-9

echo 'usage: make [changelog|clean|commit|cover|doc|gh-pages|lint|publish|superclean|test]'
'''
            )

    def test_clean(self):
        test_files = create_test_files([
            ('Makefile', 'include Makefile.base'),
            ('Makefile.base', MAKEFILE_BASE)
        ])
        with test_files as test_dir:
            self.assert_make_output(
                subprocess.check_output(['make', 'clean', '-n'], env={}, cwd=test_dir, stderr=subprocess.STDOUT, encoding='utf-8'),
                '''\
rm -rf build/ dist/ .coverage src/*.egg-info $(find src -name __pycache__)
'''
            )

    def test_superclean(self):
        test_files = create_test_files([
            ('Makefile', 'include Makefile.base'),
            ('Makefile.base', MAKEFILE_BASE)
        ])
        with test_files as test_dir:
            self.assert_make_output(
                subprocess.check_output(['make', 'superclean', '-n'], env={}, cwd=test_dir, stderr=subprocess.STDOUT, encoding='utf-8'),
                '''\
rm -rf build/ dist/ .coverage src/*.egg-info $(find src -name __pycache__)
docker rmi -f python:3.9 python:3.10-rc python:3.8 python:3.7 python:3.6
'''
            )

    def test_test(self):
        test_files = create_test_files([
            ('Makefile', 'include Makefile.base'),
            ('Makefile.base', MAKEFILE_BASE)
        ])
        with test_files as test_dir:
            # Check initial make test commands
            self.assert_make_output(
                subprocess.check_output(['make', 'test', '-n'], env={}, cwd=test_dir, stderr=subprocess.STDOUT, encoding='utf-8'),
                '''\
if [ "$(docker images -q python:3.9)" = "" ]; then docker pull -q python:3.9; fi
docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.9 python3 -m venv build/venv/test-python-3-9
docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.9 build/venv/test-python-3-9/bin/pip -q --no-cache-dir --disable-pip-version-check install --progress-bar off --upgrade pip setuptools wheel
docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.9 build/venv/test-python-3-9/bin/pip --no-cache-dir --disable-pip-version-check install --progress-bar off -e .
touch build/venv/test-python-3-9.build
docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.9 build/venv/test-python-3-9/bin/python3 -m unittest discover -v -t src -s src/tests
if [ "$(docker images -q python:3.10-rc)" = "" ]; then docker pull -q python:3.10-rc; fi
docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.10-rc python3 -m venv build/venv/test-python-3-10-rc
docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.10-rc build/venv/test-python-3-10-rc/bin/pip -q --no-cache-dir --disable-pip-version-check install --progress-bar off --upgrade pip setuptools wheel
docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.10-rc build/venv/test-python-3-10-rc/bin/pip --no-cache-dir --disable-pip-version-check install --progress-bar off -e .
touch build/venv/test-python-3-10-rc.build
docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.10-rc build/venv/test-python-3-10-rc/bin/python3 -m unittest discover -v -t src -s src/tests
if [ "$(docker images -q python:3.8)" = "" ]; then docker pull -q python:3.8; fi
docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.8 python3 -m venv build/venv/test-python-3-8
docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.8 build/venv/test-python-3-8/bin/pip -q --no-cache-dir --disable-pip-version-check install --progress-bar off --upgrade pip setuptools wheel
docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.8 build/venv/test-python-3-8/bin/pip --no-cache-dir --disable-pip-version-check install --progress-bar off -e .
touch build/venv/test-python-3-8.build
docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.8 build/venv/test-python-3-8/bin/python3 -m unittest discover -v -t src -s src/tests
if [ "$(docker images -q python:3.7)" = "" ]; then docker pull -q python:3.7; fi
docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.7 python3 -m venv build/venv/test-python-3-7
docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.7 build/venv/test-python-3-7/bin/pip -q --no-cache-dir --disable-pip-version-check install --progress-bar off --upgrade pip setuptools wheel
docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.7 build/venv/test-python-3-7/bin/pip --no-cache-dir --disable-pip-version-check install --progress-bar off -e .
touch build/venv/test-python-3-7.build
docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.7 build/venv/test-python-3-7/bin/python3 -m unittest discover -v -t src -s src/tests
if [ "$(docker images -q python:3.6)" = "" ]; then docker pull -q python:3.6; fi
docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.6 python3 -m venv build/venv/test-python-3-6
docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.6 build/venv/test-python-3-6/bin/pip -q --no-cache-dir --disable-pip-version-check install --progress-bar off --upgrade pip setuptools wheel
docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.6 build/venv/test-python-3-6/bin/pip --no-cache-dir --disable-pip-version-check install --progress-bar off -e .
touch build/venv/test-python-3-6.build
docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.6 build/venv/test-python-3-6/bin/python3 -m unittest discover -v -t src -s src/tests
'''
            )

            # Touch the environment build sentinels
            os.makedirs(os.path.join(test_dir, 'build', 'venv'))
            Path(os.path.join(test_dir, 'build', 'venv', 'test-python-3-9.build')).touch()
            Path(os.path.join(test_dir, 'build', 'venv', 'test-python-3-10-rc.build')).touch()
            Path(os.path.join(test_dir, 'build', 'venv', 'test-python-3-8.build')).touch()
            Path(os.path.join(test_dir, 'build', 'venv', 'test-python-3-7.build')).touch()
            Path(os.path.join(test_dir, 'build', 'venv', 'test-python-3-6.build')).touch()

            # Check subsequent make test commands
            self.assert_make_output(
                subprocess.check_output(['make', 'test', '-n'], env={}, cwd=test_dir, stderr=subprocess.STDOUT, encoding='utf-8'),
                '''\
docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.9 build/venv/test-python-3-9/bin/python3 -m unittest discover -v -t src -s src/tests
docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.10-rc build/venv/test-python-3-10-rc/bin/python3 -m unittest discover -v -t src -s src/tests
docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.8 build/venv/test-python-3-8/bin/python3 -m unittest discover -v -t src -s src/tests
docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.7 build/venv/test-python-3-7/bin/python3 -m unittest discover -v -t src -s src/tests
docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.6 build/venv/test-python-3-6/bin/python3 -m unittest discover -v -t src -s src/tests
'''
            )

    def test_test_exclude(self):
        test_files = create_test_files([
            (
                'Makefile',
                '''\
PYTHON_IMAGES_EXCLUDE := python:3.6
include Makefile.base
'''
            ),
            ('Makefile.base', MAKEFILE_BASE)
        ])
        with test_files as test_dir:
            # Touch the environment build sentinels
            os.makedirs(os.path.join(test_dir, 'build', 'venv'))
            Path(os.path.join(test_dir, 'build', 'venv', 'test-python-3-9.build')).touch()
            Path(os.path.join(test_dir, 'build', 'venv', 'test-python-3-10-rc.build')).touch()
            Path(os.path.join(test_dir, 'build', 'venv', 'test-python-3-8.build')).touch()
            Path(os.path.join(test_dir, 'build', 'venv', 'test-python-3-7.build')).touch()
            Path(os.path.join(test_dir, 'build', 'venv', 'test-python-3-6.build')).touch()

            # Check subsequent make test commands
            self.assert_make_output(
                subprocess.check_output(['make', 'test', '-n'], env={}, cwd=test_dir, stderr=subprocess.STDOUT, encoding='utf-8'),
                '''\
docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.9 build/venv/test-python-3-9/bin/python3 -m unittest discover -v -t src -s src/tests
docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.10-rc build/venv/test-python-3-10-rc/bin/python3 -m unittest discover -v -t src -s src/tests
docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.8 build/venv/test-python-3-8/bin/python3 -m unittest discover -v -t src -s src/tests
docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.7 build/venv/test-python-3-7/bin/python3 -m unittest discover -v -t src -s src/tests
'''
            )

    def test_cover(self):
        test_files = create_test_files([
            ('Makefile', 'include Makefile.base'),
            ('Makefile.base', MAKEFILE_BASE)
        ])
        with test_files as test_dir:
            # Check initial make cover commands
            self.assert_make_output(
                subprocess.check_output(['make', 'cover', '-n'], env={}, cwd=test_dir, stderr=subprocess.STDOUT, encoding='utf-8'),
                '''\
if [ "$(docker images -q python:3.9)" = "" ]; then docker pull -q python:3.9; fi
docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.9 python3 -m venv build/venv/cover-python-3-9
docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.9 build/venv/cover-python-3-9/bin/pip -q --no-cache-dir --disable-pip-version-check install --progress-bar off --upgrade pip setuptools wheel
docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.9 build/venv/cover-python-3-9/bin/pip --no-cache-dir --disable-pip-version-check install --progress-bar off -e . coverage=="X.X.X"
touch build/venv/cover-python-3-9.build
docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.9 build/venv/cover-python-3-9/bin/python3 -m coverage run --branch --source src -m unittest discover -v -t src -s src/tests
docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.9 build/venv/cover-python-3-9/bin/python3 -m coverage html -d build/coverage
docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.9 build/venv/cover-python-3-9/bin/python3 -m coverage report --fail-under 100
'''
            )

            # Touch the environment build sentinels
            os.makedirs(os.path.join(test_dir, 'build', 'venv'))
            Path(os.path.join(test_dir, 'build', 'venv', 'cover-python-3-9.build')).touch()

            # Check subsequent make cover commands
            self.assert_make_output(
                subprocess.check_output(['make', 'cover', '-n'], env={}, cwd=test_dir, stderr=subprocess.STDOUT, encoding='utf-8'),
                '''\
docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.9 build/venv/cover-python-3-9/bin/python3 -m coverage run --branch --source src -m unittest discover -v -t src -s src/tests
docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.9 build/venv/cover-python-3-9/bin/python3 -m coverage html -d build/coverage
docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.9 build/venv/cover-python-3-9/bin/python3 -m coverage report --fail-under 100
'''
            )

    def test_lint(self):
        test_files = create_test_files([
            ('Makefile', 'include Makefile.base'),
            ('Makefile.base', MAKEFILE_BASE)
        ])
        with test_files as test_dir:
            # Check initial make lint commands
            self.assert_make_output(
                subprocess.check_output(['make', 'lint', '-n'], env={}, cwd=test_dir, stderr=subprocess.STDOUT, encoding='utf-8'),
                '''\
if [ "$(docker images -q python:3.9)" = "" ]; then docker pull -q python:3.9; fi
docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.9 python3 -m venv build/venv/lint-python-3-9
docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.9 build/venv/lint-python-3-9/bin/pip -q --no-cache-dir --disable-pip-version-check install --progress-bar off --upgrade pip setuptools wheel
docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.9 build/venv/lint-python-3-9/bin/pip --no-cache-dir --disable-pip-version-check install --progress-bar off -e . pylint=="X.X.X"
touch build/venv/lint-python-3-9.build
docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.9 build/venv/lint-python-3-9/bin/python3 -m pylint -j 0 setup.py src
'''
            )

            # Touch the environment build sentinels
            os.makedirs(os.path.join(test_dir, 'build', 'venv'))
            Path(os.path.join(test_dir, 'build', 'venv', 'lint-python-3-9.build')).touch()

            # Check subsequent make lint commands
            self.assert_make_output(
                subprocess.check_output(['make', 'lint', '-n'], env={}, cwd=test_dir, stderr=subprocess.STDOUT, encoding='utf-8'),
                '''\
docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.9 build/venv/lint-python-3-9/bin/python3 -m pylint -j 0 setup.py src
'''
            )

    def test_doc(self):
        test_files = create_test_files([
            (
                'Makefile',
                '''\
SPHINX_DOC := doc
include Makefile.base
'''
            ),
            ('Makefile.base', MAKEFILE_BASE)
        ])
        with test_files as test_dir:
            # Check initial make doc commands
            self.assert_make_output(
                subprocess.check_output(['make', 'doc', '-n'], env={}, cwd=test_dir, stderr=subprocess.STDOUT, encoding='utf-8'),
                '''\
if [ "$(docker images -q python:3.9)" = "" ]; then docker pull -q python:3.9; fi
docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.9 python3 -m venv build/venv/doc-python-3-9
docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.9 build/venv/doc-python-3-9/bin/pip -q --no-cache-dir --disable-pip-version-check install --progress-bar off --upgrade pip setuptools wheel
docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.9 build/venv/doc-python-3-9/bin/pip --no-cache-dir --disable-pip-version-check install --progress-bar off -e . sphinx=="X.X.X" sphinx_rtd_theme=="X.X.X"
touch build/venv/doc-python-3-9.build
docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.9 build/venv/doc-python-3-9/bin/sphinx-build -W -a -b doctest -d build/doc/doctrees doc build/doc/doctest
docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.9 build/venv/doc-python-3-9/bin/sphinx-build -W -a -b html -d build/doc/doctrees doc build/doc/html
'''
            )

            # Touch the environment build sentinels
            os.makedirs(os.path.join(test_dir, 'build', 'venv'))
            Path(os.path.join(test_dir, 'build', 'venv', 'doc-python-3-9.build')).touch()

            # Check subsequent make doc commands
            self.assert_make_output(
                subprocess.check_output(['make', 'doc', '-n'], env={}, cwd=test_dir, stderr=subprocess.STDOUT, encoding='utf-8'),
                '''\
docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.9 build/venv/doc-python-3-9/bin/sphinx-build -W -a -b doctest -d build/doc/doctrees doc build/doc/doctest
docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.9 build/venv/doc-python-3-9/bin/sphinx-build -W -a -b html -d build/doc/doctrees doc build/doc/html
'''
            )

    def test_doc_none(self):
        test_files = create_test_files([
            ('Makefile', 'include Makefile.base'),
            ('Makefile.base', MAKEFILE_BASE)
        ])
        with test_files as test_dir:
            # Touch the environment build sentinels
            os.makedirs(os.path.join(test_dir, 'build', 'venv'))
            Path(os.path.join(test_dir, 'build', 'venv', 'doc-python-3-9.build')).touch()

            # Check subsequent make doc commands
            self.assert_make_output(
                subprocess.check_output(['make', 'doc', '-n'], env={}, cwd=test_dir, stderr=subprocess.STDOUT, encoding='utf-8'),
                '''\
make: Nothing to be done for 'doc'.
'''
            )

            # Check subsequent make doc commands
            self.assert_make_output(
                subprocess.check_output(['make', 'gh-pages', '-n'], env={}, cwd=test_dir, stderr=subprocess.STDOUT, encoding='utf-8'),
                '''\
make: Nothing to be done for 'gh-pages'.
'''
            )

    def test_gh_pages(self):
        test_files = create_test_files([
            (
                'Makefile',
                '''\
SPHINX_DOC := doc
include Makefile.base
'''
            ),
            ('Makefile.base', MAKEFILE_BASE)
        ])
        with test_files as test_dir:
            # Touch the environment build sentinels
            os.makedirs(os.path.join(test_dir, 'build', 'venv'))
            Path(os.path.join(test_dir, 'build', 'venv', 'doc-python-3-9.build')).touch()

            # Check make gh-pages commands
            output = subprocess.check_output(['make', 'gh-pages', '-n'], env={}, cwd=test_dir, stderr=subprocess.STDOUT, encoding='utf-8')
            output = re.sub(r'../tmp.*?\.gh-pages\b', '../tmp.gh-pages', output)
            self.assert_make_output(
                output,
                '''\
rm -rf build/ dist/ .coverage src/*.egg-info $(find src -name __pycache__)
docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.9 build/venv/doc-python-3-9/bin/sphinx-build -W -a -b doctest -d build/doc/doctrees doc build/doc/doctest
docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.9 build/venv/doc-python-3-9/bin/sphinx-build -W -a -b html -d build/doc/doctrees doc build/doc/html
if [ ! -d ../tmp.gh-pages ]; then git clone -b gh-pages `git config --get remote.origin.url` ../tmp.gh-pages; fi
cd ../tmp.gh-pages && git pull
rsync -rv --delete --exclude=.git/ build/doc/html/ ../tmp.gh-pages
'''
            )

    def test_commit(self):
        test_files = create_test_files([
            ('Makefile', 'include Makefile.base'),
            ('Makefile.base', MAKEFILE_BASE)
        ])
        with test_files as test_dir:
            # Touch the environment build sentinels
            os.makedirs(os.path.join(test_dir, 'build', 'venv'))
            Path(os.path.join(test_dir, 'build', 'venv', 'cover-python-3-9.build')).touch()
            Path(os.path.join(test_dir, 'build', 'venv', 'doc-python-3-9.build')).touch()
            Path(os.path.join(test_dir, 'build', 'venv', 'lint-python-3-9.build')).touch()
            Path(os.path.join(test_dir, 'build', 'venv', 'test-python-3-9.build')).touch()
            Path(os.path.join(test_dir, 'build', 'venv', 'test-python-3-10-rc.build')).touch()
            Path(os.path.join(test_dir, 'build', 'venv', 'test-python-3-8.build')).touch()
            Path(os.path.join(test_dir, 'build', 'venv', 'test-python-3-7.build')).touch()
            Path(os.path.join(test_dir, 'build', 'venv', 'test-python-3-6.build')).touch()

            # Check make commit commands
            self.assert_make_output(
                subprocess.check_output(['make', 'commit', '-n'], env={}, cwd=test_dir, stderr=subprocess.STDOUT, encoding='utf-8'),
                '''\
docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.9 build/venv/test-python-3-9/bin/python3 -m unittest discover -v -t src -s src/tests
docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.10-rc build/venv/test-python-3-10-rc/bin/python3 -m unittest discover -v -t src -s src/tests
docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.8 build/venv/test-python-3-8/bin/python3 -m unittest discover -v -t src -s src/tests
docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.7 build/venv/test-python-3-7/bin/python3 -m unittest discover -v -t src -s src/tests
docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.6 build/venv/test-python-3-6/bin/python3 -m unittest discover -v -t src -s src/tests
docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.9 build/venv/lint-python-3-9/bin/python3 -m pylint -j 0 setup.py src
docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.9 build/venv/cover-python-3-9/bin/python3 -m coverage run --branch --source src -m unittest discover -v -t src -s src/tests
docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.9 build/venv/cover-python-3-9/bin/python3 -m coverage html -d build/coverage
docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.9 build/venv/cover-python-3-9/bin/python3 -m coverage report --fail-under 100
'''
            )

    def test_commit_no_docker(self):
        test_files = create_test_files([
            ('Makefile', 'include Makefile.base'),
            ('Makefile.base', MAKEFILE_BASE)
        ])
        with test_files as test_dir:
            self.assert_make_output(
                subprocess.check_output(['make', 'commit', '-n'], env={'NO_DOCKER': '1'}, cwd=test_dir, stderr=subprocess.STDOUT, encoding='utf-8'),
                '''\
python3 -m venv build/venv/test-no-docker
build/venv/test-no-docker/bin/pip -q --no-cache-dir --disable-pip-version-check install --progress-bar off --upgrade pip setuptools wheel
build/venv/test-no-docker/bin/pip --no-cache-dir --disable-pip-version-check install --progress-bar off -e .
touch build/venv/test-no-docker.build
build/venv/test-no-docker/bin/python3 -m unittest discover -v -t src -s src/tests
python3 -m venv build/venv/lint-no-docker
build/venv/lint-no-docker/bin/pip -q --no-cache-dir --disable-pip-version-check install --progress-bar off --upgrade pip setuptools wheel
build/venv/lint-no-docker/bin/pip --no-cache-dir --disable-pip-version-check install --progress-bar off -e . pylint=="X.X.X"
touch build/venv/lint-no-docker.build
build/venv/lint-no-docker/bin/python3 -m pylint -j 0 setup.py src
python3 -m venv build/venv/cover-no-docker
build/venv/cover-no-docker/bin/pip -q --no-cache-dir --disable-pip-version-check install --progress-bar off --upgrade pip setuptools wheel
build/venv/cover-no-docker/bin/pip --no-cache-dir --disable-pip-version-check install --progress-bar off -e . coverage=="X.X.X"
touch build/venv/cover-no-docker.build
build/venv/cover-no-docker/bin/python3 -m coverage run --branch --source src -m unittest discover -v -t src -s src/tests
build/venv/cover-no-docker/bin/python3 -m coverage html -d build/coverage
build/venv/cover-no-docker/bin/python3 -m coverage report --fail-under 100
'''
            )

    def test_commit_overrides(self):
        test_files = create_test_files([
            (
                'Makefile',
                '''\
PYTHON_IMAGES := \
    python:3.9 \
    python:3.8 \
    python:3.7

SPHINX_DOC := doc

include Makefile.base
'''
            ),
            ('Makefile.base', MAKEFILE_BASE)
        ])
        with test_files as test_dir:
            self.assert_make_output(
                subprocess.check_output(
                    ['make', 'commit', '-n'],
                    env = {
                        'PIP_ARGS': '--bogus-pip-pargs',
                        'PIP_INSTALL_ARGS': '--bogus-pip-install-args',
                        'COVERAGE_VERSION': 'bogus-coverage-version',
                        'COVERAGE_REPORT_ARGS': '--bogus-coverage-report-args',
                        'PYLINT_VERSION': 'bogus-pylint-version',
                        'PYLINT_ARGS': '--bogus-pylint-args',
                        'SPHINX_VERSION': 'bogus-sphinx-version',
                        'SPHINX_RTD_THEME_VERSION': 'bogus-sphinx-rtd-theme-version',
                        'SPHINX_ARGS': '--bogus-sphinx-args',
                        'SPHINX_DOC': 'bogus-sphinx-doc',
                        'TESTS_REQUIRE': '"foobar >= 1.0"',
                        'NO_DOCKER': ''
                    },
                    cwd=test_dir, stderr=subprocess.STDOUT, encoding='utf-8'
                ),
                '''\
if [ "$(docker images -q python:3.9)" = "" ]; then docker pull -q python:3.9; fi
docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.9 python3 -m venv build/venv/test-python-3-9
docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.9 build/venv/test-python-3-9/bin/pip -q --bogus-pip-pargs install --bogus-pip-install-args --upgrade pip setuptools wheel
docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.9 build/venv/test-python-3-9/bin/pip --bogus-pip-pargs install --bogus-pip-install-args -e . "foobar >= 1.0"
touch build/venv/test-python-3-9.build
docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.9 build/venv/test-python-3-9/bin/python3 -m unittest discover -v -t src -s src/tests
if [ "$(docker images -q python:3.8)" = "" ]; then docker pull -q python:3.8; fi
docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.8 python3 -m venv build/venv/test-python-3-8
docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.8 build/venv/test-python-3-8/bin/pip -q --bogus-pip-pargs install --bogus-pip-install-args --upgrade pip setuptools wheel
docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.8 build/venv/test-python-3-8/bin/pip --bogus-pip-pargs install --bogus-pip-install-args -e . "foobar >= 1.0"
touch build/venv/test-python-3-8.build
docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.8 build/venv/test-python-3-8/bin/python3 -m unittest discover -v -t src -s src/tests
if [ "$(docker images -q python:3.7)" = "" ]; then docker pull -q python:3.7; fi
docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.7 python3 -m venv build/venv/test-python-3-7
docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.7 build/venv/test-python-3-7/bin/pip -q --bogus-pip-pargs install --bogus-pip-install-args --upgrade pip setuptools wheel
docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.7 build/venv/test-python-3-7/bin/pip --bogus-pip-pargs install --bogus-pip-install-args -e . "foobar >= 1.0"
touch build/venv/test-python-3-7.build
docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.7 build/venv/test-python-3-7/bin/python3 -m unittest discover -v -t src -s src/tests
if [ "$(docker images -q python:3.9)" = "" ]; then docker pull -q python:3.9; fi
docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.9 python3 -m venv build/venv/lint-python-3-9
docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.9 build/venv/lint-python-3-9/bin/pip -q --bogus-pip-pargs install --bogus-pip-install-args --upgrade pip setuptools wheel
docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.9 build/venv/lint-python-3-9/bin/pip --bogus-pip-pargs install --bogus-pip-install-args -e . pylint=="bogus-pylint-version"
touch build/venv/lint-python-3-9.build
docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.9 build/venv/lint-python-3-9/bin/python3 -m pylint --bogus-pylint-args setup.py src
if [ "$(docker images -q python:3.9)" = "" ]; then docker pull -q python:3.9; fi
docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.9 python3 -m venv build/venv/doc-python-3-9
docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.9 build/venv/doc-python-3-9/bin/pip -q --bogus-pip-pargs install --bogus-pip-install-args --upgrade pip setuptools wheel
docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.9 build/venv/doc-python-3-9/bin/pip --bogus-pip-pargs install --bogus-pip-install-args -e . sphinx=="bogus-sphinx-version" sphinx_rtd_theme=="bogus-sphinx-rtd-theme-version"
touch build/venv/doc-python-3-9.build
docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.9 build/venv/doc-python-3-9/bin/sphinx-build --bogus-sphinx-args -b doctest -d build/doc/doctrees doc build/doc/doctest
docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.9 build/venv/doc-python-3-9/bin/sphinx-build --bogus-sphinx-args -b html -d build/doc/doctrees doc build/doc/html
if [ "$(docker images -q python:3.9)" = "" ]; then docker pull -q python:3.9; fi
docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.9 python3 -m venv build/venv/cover-python-3-9
docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.9 build/venv/cover-python-3-9/bin/pip -q --bogus-pip-pargs install --bogus-pip-install-args --upgrade pip setuptools wheel
docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.9 build/venv/cover-python-3-9/bin/pip --bogus-pip-pargs install --bogus-pip-install-args -e . coverage=="bogus-coverage-version" "foobar >= 1.0"
touch build/venv/cover-python-3-9.build
docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.9 build/venv/cover-python-3-9/bin/python3 -m coverage run --branch --source src -m unittest discover -v -t src -s src/tests
docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.9 build/venv/cover-python-3-9/bin/python3 -m coverage html -d build/coverage
docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.9 build/venv/cover-python-3-9/bin/python3 -m coverage report --bogus-coverage-report-args
'''
            )

    def test_publish(self):
        test_files = create_test_files([
            ('Makefile', 'include Makefile.base'),
            ('Makefile.base', MAKEFILE_BASE)
        ])
        with test_files as test_dir:
            # Touch the environment build sentinels
            os.makedirs(os.path.join(test_dir, 'build', 'venv'))
            Path(os.path.join(test_dir, 'build', 'venv', 'cover-python-3-9.build')).touch()
            Path(os.path.join(test_dir, 'build', 'venv', 'doc-python-3-9.build')).touch()
            Path(os.path.join(test_dir, 'build', 'venv', 'lint-python-3-9.build')).touch()
            Path(os.path.join(test_dir, 'build', 'venv', 'test-python-3-9.build')).touch()
            Path(os.path.join(test_dir, 'build', 'venv', 'test-python-3-10-rc.build')).touch()
            Path(os.path.join(test_dir, 'build', 'venv', 'test-python-3-8.build')).touch()
            Path(os.path.join(test_dir, 'build', 'venv', 'test-python-3-7.build')).touch()
            Path(os.path.join(test_dir, 'build', 'venv', 'test-python-3-6.build')).touch()

            # Check make publish commands
            self.assert_make_output(
                subprocess.check_output(['make', 'publish', '-n'], env={}, cwd=test_dir, stderr=subprocess.STDOUT, encoding='utf-8'),
                '''\
rm -rf build/ dist/ .coverage src/*.egg-info $(find src -name __pycache__)
docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.9 build/venv/test-python-3-9/bin/python3 -m unittest discover -v -t src -s src/tests
docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.10-rc build/venv/test-python-3-10-rc/bin/python3 -m unittest discover -v -t src -s src/tests
docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.8 build/venv/test-python-3-8/bin/python3 -m unittest discover -v -t src -s src/tests
docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.7 build/venv/test-python-3-7/bin/python3 -m unittest discover -v -t src -s src/tests
docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.6 build/venv/test-python-3-6/bin/python3 -m unittest discover -v -t src -s src/tests
docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.9 build/venv/lint-python-3-9/bin/python3 -m pylint -j 0 setup.py src
docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.9 build/venv/cover-python-3-9/bin/python3 -m coverage run --branch --source src -m unittest discover -v -t src -s src/tests
docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.9 build/venv/cover-python-3-9/bin/python3 -m coverage html -d build/coverage
docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.9 build/venv/cover-python-3-9/bin/python3 -m coverage report --fail-under 100
if [ "$(docker images -q python:3.9)" = "" ]; then docker pull -q python:3.9; fi
docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.9 python3 -m venv build/venv/publish-python-3-9
docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.9 build/venv/publish-python-3-9/bin/pip -q --no-cache-dir --disable-pip-version-check install --progress-bar off --upgrade pip setuptools wheel
docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.9 build/venv/publish-python-3-9/bin/pip --no-cache-dir --disable-pip-version-check install --progress-bar off twine
touch build/venv/publish-python-3-9.build
docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.9 build/venv/publish-python-3-9/bin/python3 setup.py sdist
docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.9 build/venv/publish-python-3-9/bin/twine check dist/*.tar.gz
docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.9 build/venv/publish-python-3-9/bin/twine upload dist/*.tar.gz
'''
            )

            # Touch the environment build sentinels
            Path(os.path.join(test_dir, 'build', 'venv', 'publish-python-3-9.build')).touch()

            # Check subsequent make publish commands
            self.assert_make_output(
                subprocess.check_output(['make', 'publish', '-n'], env={}, cwd=test_dir, stderr=subprocess.STDOUT, encoding='utf-8'),
                '''\
rm -rf build/ dist/ .coverage src/*.egg-info $(find src -name __pycache__)
docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.9 build/venv/test-python-3-9/bin/python3 -m unittest discover -v -t src -s src/tests
docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.10-rc build/venv/test-python-3-10-rc/bin/python3 -m unittest discover -v -t src -s src/tests
docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.8 build/venv/test-python-3-8/bin/python3 -m unittest discover -v -t src -s src/tests
docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.7 build/venv/test-python-3-7/bin/python3 -m unittest discover -v -t src -s src/tests
docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.6 build/venv/test-python-3-6/bin/python3 -m unittest discover -v -t src -s src/tests
docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.9 build/venv/lint-python-3-9/bin/python3 -m pylint -j 0 setup.py src
docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.9 build/venv/cover-python-3-9/bin/python3 -m coverage run --branch --source src -m unittest discover -v -t src -s src/tests
docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.9 build/venv/cover-python-3-9/bin/python3 -m coverage html -d build/coverage
docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.9 build/venv/cover-python-3-9/bin/python3 -m coverage report --fail-under 100
docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.9 build/venv/publish-python-3-9/bin/python3 setup.py sdist
docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.9 build/venv/publish-python-3-9/bin/twine check dist/*.tar.gz
docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.9 build/venv/publish-python-3-9/bin/twine upload dist/*.tar.gz
'''
            )

    def test_changelog(self):
        test_files = create_test_files([
            ('Makefile', 'include Makefile.base'),
            ('Makefile.base', MAKEFILE_BASE)
        ])
        with test_files as test_dir:
            # Touch the environment build sentinels
            os.makedirs(os.path.join(test_dir, 'build', 'venv'))
            Path(os.path.join(test_dir, 'build', 'venv', 'changelog-python-3-9.build')).touch()

            # Check subsequent make publish commands
            self.assert_make_output(
                subprocess.check_output(['make', 'changelog', '-n'], env={}, cwd=test_dir, stderr=subprocess.STDOUT, encoding='utf-8'),
                '''\
docker run -i --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd` python:3.9 build/venv/changelog-python-3-9/bin/simple-git-changelog
'''
            )
