# Licensed under the MIT License
# https://github.com/craigahobbs/python-build/blob/master/LICENSE

"""
Python Build makefile unit tests
"""

# pylint: disable=line-too-long, missing-function-docstring

import os
from pathlib import Path
import re
import subprocess
from tempfile import TemporaryDirectory
import unittest


# Read the base makefile
with open('Makefile.base', 'r') as file_makefile_base:
    MAKEFILE_BASE = file_makefile_base.read()


# The default Python Build makefile
DEFAULT_MAKEFILE = '''\
PYTHON_VERSIONS := \
    3.9 \
    3.8 \
    3.7

SPHINX_DOC := doc

include Makefile.base
'''


# Helper function to create a list of files in a temporary directory
def create_test_files(file_defs):
    tempdir = TemporaryDirectory()
    for path_parts, content in file_defs:
        if isinstance(path_parts, str):
            path_parts = [path_parts]
        path = os.path.join(tempdir.name, *path_parts)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as file_:
            file_.write(content)
    return tempdir


class PythonBuildTest(unittest.TestCase):
    """
    Python Build makefile unit tests
    """

    @staticmethod
    def check_output(args, cwd, env=None):
        if env is None:
            env = {'NO_DOCKER': ''}
        return subprocess.check_output(args, env=env, cwd=cwd, stderr=subprocess.STDOUT, encoding='utf-8')

    def assert_make_output(self, actual, expected):
        actual_clean = actual

        # Cleanup make message for macOS
        actual_clean = re.sub(r'^(make: Nothing to be done for )`', r"\1'", actual_clean, flags=re.MULTILINE)

        # Cleanup leading tabs for macOS
        actual_clean = re.sub(r'^\t\t', r'\t', actual_clean, flags=re.MULTILINE)

        self.assertEqual(actual_clean, expected)

    def test_help(self):
        test_files = create_test_files([
            ('Makefile', DEFAULT_MAKEFILE),
            ('Makefile.base', MAKEFILE_BASE)
        ])
        with test_files as test_dir:
            self.assert_make_output(
                self.check_output(['make', '-n'], test_dir),
                '''\
echo 'usage: make [clean|commit|cover|doc|gh-pages|lint|test|twine]'
'''
            )

    def test_clean(self):
        test_files = create_test_files([
            ('Makefile', DEFAULT_MAKEFILE),
            ('Makefile.base', MAKEFILE_BASE)
        ])
        with test_files as test_dir:
            self.assert_make_output(
                self.check_output(['make', 'clean', '-n'], test_dir),
                '''\
rm -rf \\
	build \\
	.coverage \\
	$(find src -name __pycache__) \\
	dist/ \\
	src/*.egg-info \\
	*.eggs
'''
            )

    def test_superclean(self):
        test_files = create_test_files([
            ('Makefile', DEFAULT_MAKEFILE),
            ('Makefile.base', MAKEFILE_BASE)
        ])
        with test_files as test_dir:
            self.assert_make_output(
                self.check_output(['make', 'superclean', '-n'], test_dir),
                '''\
rm -rf \\
	build \\
	.coverage \\
	$(find src -name __pycache__) \\
	dist/ \\
	src/*.egg-info \\
	*.eggs
docker rmi -f python:3.9 python:3.8 python:3.7
'''
            )

    def test_test(self):
        test_files = create_test_files([
            ('Makefile', DEFAULT_MAKEFILE),
            ('Makefile.base', MAKEFILE_BASE)
        ])
        with test_files as test_dir:
            # Check initial make test commands
            self.assert_make_output(
                self.check_output(['make', 'test', '-n'], cwd=test_dir),
                '''\
docker pull -q python:3.9
docker run --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd`  python:3.9 python3 -m venv build/venv/test-python-3.9
docker run --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd`  python:3.9 build/venv/test-python-3.9/bin/pip -q --no-cache-dir --disable-pip-version-check install --progress-bar off --upgrade pip setuptools wheel
docker run --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd`  python:3.9 build/venv/test-python-3.9/bin/pip --no-cache-dir --disable-pip-version-check install --progress-bar off  -e . -e .[tests]
touch build/venv/test-python-3.9.build
docker run --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd`  python:3.9 build/venv/test-python-3.9/bin/python3 -m unittest discover -v -t src -s src/tests
docker pull -q python:3.8
docker run --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd`  python:3.8 python3 -m venv build/venv/test-python-3.8
docker run --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd`  python:3.8 build/venv/test-python-3.8/bin/pip -q --no-cache-dir --disable-pip-version-check install --progress-bar off --upgrade pip setuptools wheel
docker run --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd`  python:3.8 build/venv/test-python-3.8/bin/pip --no-cache-dir --disable-pip-version-check install --progress-bar off  -e . -e .[tests]
touch build/venv/test-python-3.8.build
docker run --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd`  python:3.8 build/venv/test-python-3.8/bin/python3 -m unittest discover -v -t src -s src/tests
docker pull -q python:3.7
docker run --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd`  python:3.7 python3 -m venv build/venv/test-python-3.7
docker run --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd`  python:3.7 build/venv/test-python-3.7/bin/pip -q --no-cache-dir --disable-pip-version-check install --progress-bar off --upgrade pip setuptools wheel
docker run --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd`  python:3.7 build/venv/test-python-3.7/bin/pip --no-cache-dir --disable-pip-version-check install --progress-bar off  -e . -e .[tests]
touch build/venv/test-python-3.7.build
docker run --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd`  python:3.7 build/venv/test-python-3.7/bin/python3 -m unittest discover -v -t src -s src/tests
'''
            )

            # Touch the environment build sentinels
            os.makedirs(os.path.join(test_dir, 'build', 'venv'))
            Path(os.path.join(test_dir, 'build', 'venv', 'test-python-3.9.build')).touch()
            Path(os.path.join(test_dir, 'build', 'venv', 'test-python-3.8.build')).touch()
            Path(os.path.join(test_dir, 'build', 'venv', 'test-python-3.7.build')).touch()

            # Check subsequent make test commands
            self.assert_make_output(
                self.check_output(['make', 'test', '-n'], test_dir),
                '''\
docker run --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd`  python:3.9 build/venv/test-python-3.9/bin/python3 -m unittest discover -v -t src -s src/tests
docker run --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd`  python:3.8 build/venv/test-python-3.8/bin/python3 -m unittest discover -v -t src -s src/tests
docker run --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd`  python:3.7 build/venv/test-python-3.7/bin/python3 -m unittest discover -v -t src -s src/tests
'''
            )

    def test_cover(self):
        test_files = create_test_files([
            ('Makefile', DEFAULT_MAKEFILE),
            ('Makefile.base', MAKEFILE_BASE)
        ])
        with test_files as test_dir:
            # Check initial make cover commands
            self.assert_make_output(
                self.check_output(['make', 'cover', '-n'], test_dir),
                '''\
docker pull -q python:3.9
docker run --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd`  python:3.9 python3 -m venv build/venv/cover-python-3.9
docker run --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd`  python:3.9 build/venv/cover-python-3.9/bin/pip -q --no-cache-dir --disable-pip-version-check install --progress-bar off --upgrade pip setuptools wheel
docker run --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd`  python:3.9 build/venv/cover-python-3.9/bin/pip --no-cache-dir --disable-pip-version-check install --progress-bar off  -e . -e .[tests] coverage==5.5
touch build/venv/cover-python-3.9.build
docker run --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd`  python:3.9 build/venv/cover-python-3.9/bin/python3 -m coverage run --branch --source src -m unittest discover -v -t src -s src/tests
docker run --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd`  python:3.9 build/venv/cover-python-3.9/bin/python3 -m coverage html -d build/coverage
docker run --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd`  python:3.9 build/venv/cover-python-3.9/bin/python3 -m coverage report --fail-under 100
'''
            )

            # Touch the environment build sentinels
            os.makedirs(os.path.join(test_dir, 'build', 'venv'))
            Path(os.path.join(test_dir, 'build', 'venv', 'cover-python-3.9.build')).touch()

            # Check subsequent make cover commands
            self.assert_make_output(
                self.check_output(['make', 'cover', '-n'], test_dir),
                '''\
docker run --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd`  python:3.9 build/venv/cover-python-3.9/bin/python3 -m coverage run --branch --source src -m unittest discover -v -t src -s src/tests
docker run --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd`  python:3.9 build/venv/cover-python-3.9/bin/python3 -m coverage html -d build/coverage
docker run --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd`  python:3.9 build/venv/cover-python-3.9/bin/python3 -m coverage report --fail-under 100
'''
            )

    def test_lint(self):
        test_files = create_test_files([
            ('Makefile', DEFAULT_MAKEFILE),
            ('Makefile.base', MAKEFILE_BASE)
        ])
        with test_files as test_dir:
            # Check initial make lint commands
            self.assert_make_output(
                self.check_output(['make', 'lint', '-n'], test_dir),
                '''\
docker pull -q python:3.9
docker run --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd`  python:3.9 python3 -m venv build/venv/lint-python-3.9
docker run --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd`  python:3.9 build/venv/lint-python-3.9/bin/pip -q --no-cache-dir --disable-pip-version-check install --progress-bar off --upgrade pip setuptools wheel
docker run --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd`  python:3.9 build/venv/lint-python-3.9/bin/pip --no-cache-dir --disable-pip-version-check install --progress-bar off  -e . pylint==2.7.2
touch build/venv/lint-python-3.9.build
docker run --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd`  python:3.9 build/venv/lint-python-3.9/bin/python3 -m pylint -j 0 setup.py src
'''
            )

            # Touch the environment build sentinels
            os.makedirs(os.path.join(test_dir, 'build', 'venv'))
            Path(os.path.join(test_dir, 'build', 'venv', 'lint-python-3.9.build')).touch()

            # Check subsequent make lint commands
            self.assert_make_output(
                self.check_output(['make', 'lint', '-n'], test_dir),
                '''\
docker run --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd`  python:3.9 build/venv/lint-python-3.9/bin/python3 -m pylint -j 0 setup.py src
'''
            )

    def test_doc(self):
        test_files = create_test_files([
            ('Makefile', DEFAULT_MAKEFILE),
            ('Makefile.base', MAKEFILE_BASE)
        ])
        with test_files as test_dir:
            # Check initial make doc commands
            self.assert_make_output(
                self.check_output(['make', 'doc', '-n'], test_dir),
                '''\
docker pull -q python:3.9
docker run --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd`  python:3.9 python3 -m venv build/venv/doc-python-3.9
docker run --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd`  python:3.9 build/venv/doc-python-3.9/bin/pip -q --no-cache-dir --disable-pip-version-check install --progress-bar off --upgrade pip setuptools wheel
docker run --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd`  python:3.9 build/venv/doc-python-3.9/bin/pip --no-cache-dir --disable-pip-version-check install --progress-bar off  -e . sphinx==3.5.1 sphinx_rtd_theme==0.5.1
touch build/venv/doc-python-3.9.build
docker run --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd`  python:3.9 build/venv/doc-python-3.9/bin/sphinx-build -W -a -b doctest -d build/doc/doctrees doc build/doc/doctest
docker run --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd`  python:3.9 build/venv/doc-python-3.9/bin/sphinx-build -W -a -b html -d build/doc/doctrees doc build/doc/html
'''
            )

            # Touch the environment build sentinels
            os.makedirs(os.path.join(test_dir, 'build', 'venv'))
            Path(os.path.join(test_dir, 'build', 'venv', 'doc-python-3.9.build')).touch()

            # Check subsequent make doc commands
            self.assert_make_output(
                self.check_output(['make', 'doc', '-n'], test_dir),
                '''\
docker run --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd`  python:3.9 build/venv/doc-python-3.9/bin/sphinx-build -W -a -b doctest -d build/doc/doctrees doc build/doc/doctest
docker run --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd`  python:3.9 build/venv/doc-python-3.9/bin/sphinx-build -W -a -b html -d build/doc/doctrees doc build/doc/html
'''
            )

    def test_doc_none(self):
        test_files = create_test_files([
            (
                'Makefile',
                '''\
PYTHON_VERSIONS := \
    3.9 \
    3.8 \
    3.7

include Makefile.base
'''
            ),
            ('Makefile.base', MAKEFILE_BASE)
        ])
        with test_files as test_dir:
            # Touch the environment build sentinels
            os.makedirs(os.path.join(test_dir, 'build', 'venv'))
            Path(os.path.join(test_dir, 'build', 'venv', 'doc-python-3.9.build')).touch()

            # Check subsequent make doc commands
            self.assert_make_output(
                self.check_output(['make', 'doc', '-n'], test_dir),
                '''\
make: Nothing to be done for 'doc'.
'''
            )

            # Check subsequent make doc commands
            self.assert_make_output(
                self.check_output(['make', 'gh-pages', '-n'], cwd=test_dir),
                '''\
make: Nothing to be done for 'gh-pages'.
'''
            )

    def test_gh_pages(self):
        test_files = create_test_files([
            ('Makefile', DEFAULT_MAKEFILE),
            ('Makefile.base', MAKEFILE_BASE)
        ])
        with test_files as test_dir:
            # Touch the environment build sentinels
            os.makedirs(os.path.join(test_dir, 'build', 'venv'))
            Path(os.path.join(test_dir, 'build', 'venv', 'doc-python-3.9.build')).touch()

            # Check make gh-pages commands
            output = self.check_output(['make', 'gh-pages', '-n'], test_dir)
            output = re.sub(r'../tmp.*?\.gh-pages\b', '../tmp.gh-pages', output)
            self.assert_make_output(
                output,
                '''\
rm -rf \\
	build \\
	.coverage \\
	$(find src -name __pycache__) \\
	dist/ \\
	src/*.egg-info \\
	*.eggs
docker run --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd`  python:3.9 build/venv/doc-python-3.9/bin/sphinx-build -W -a -b doctest -d build/doc/doctrees doc build/doc/doctest
docker run --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd`  python:3.9 build/venv/doc-python-3.9/bin/sphinx-build -W -a -b html -d build/doc/doctrees doc build/doc/html
if [ ! -d ../tmp.gh-pages ]; then git clone -b gh-pages `git config --get remote.origin.url` ../tmp.gh-pages; fi
cd ../tmp.gh-pages && git pull
rsync -rv --delete --exclude=.git/ build/doc/html/ ../tmp.gh-pages
'''
            )

    def test_commit(self):
        test_files = create_test_files([
            ('Makefile', DEFAULT_MAKEFILE),
            ('Makefile.base', MAKEFILE_BASE)
        ])
        with test_files as test_dir:
            # Touch the environment build sentinels
            os.makedirs(os.path.join(test_dir, 'build', 'venv'))
            Path(os.path.join(test_dir, 'build', 'venv', 'cover-python-3.9.build')).touch()
            Path(os.path.join(test_dir, 'build', 'venv', 'doc-python-3.9.build')).touch()
            Path(os.path.join(test_dir, 'build', 'venv', 'lint-python-3.9.build')).touch()
            Path(os.path.join(test_dir, 'build', 'venv', 'test-python-3.9.build')).touch()
            Path(os.path.join(test_dir, 'build', 'venv', 'test-python-3.8.build')).touch()
            Path(os.path.join(test_dir, 'build', 'venv', 'test-python-3.7.build')).touch()

            # Check make commit commands
            self.assert_make_output(
                self.check_output(['make', 'commit', '-n'], test_dir),
                '''\
docker run --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd`  python:3.9 build/venv/test-python-3.9/bin/python3 -m unittest discover -v -t src -s src/tests
docker run --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd`  python:3.8 build/venv/test-python-3.8/bin/python3 -m unittest discover -v -t src -s src/tests
docker run --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd`  python:3.7 build/venv/test-python-3.7/bin/python3 -m unittest discover -v -t src -s src/tests
docker run --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd`  python:3.9 build/venv/lint-python-3.9/bin/python3 -m pylint -j 0 setup.py src
docker run --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd`  python:3.9 build/venv/doc-python-3.9/bin/sphinx-build -W -a -b doctest -d build/doc/doctrees doc build/doc/doctest
docker run --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd`  python:3.9 build/venv/doc-python-3.9/bin/sphinx-build -W -a -b html -d build/doc/doctrees doc build/doc/html
docker run --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd`  python:3.9 build/venv/cover-python-3.9/bin/python3 -m coverage run --branch --source src -m unittest discover -v -t src -s src/tests
docker run --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd`  python:3.9 build/venv/cover-python-3.9/bin/python3 -m coverage html -d build/coverage
docker run --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd`  python:3.9 build/venv/cover-python-3.9/bin/python3 -m coverage report --fail-under 100
'''
            )

    def test_commit_no_docker(self):
        test_files = create_test_files([
            ('Makefile', DEFAULT_MAKEFILE),
            ('Makefile.base', MAKEFILE_BASE)
        ])
        with test_files as test_dir:
            # Check make commit commands
            self.assert_make_output(
                self.check_output(['make', 'commit', '-n'], test_dir, env={'NO_DOCKER': '1'}),
                '''\
python3 -m venv build/venv/test-python-3.9
build/venv/test-python-3.9/bin/pip -q --no-cache-dir --disable-pip-version-check install --progress-bar off --upgrade pip setuptools wheel
build/venv/test-python-3.9/bin/pip --no-cache-dir --disable-pip-version-check install --progress-bar off  -e . -e .[tests]
touch build/venv/test-python-3.9.build
build/venv/test-python-3.9/bin/python3 -m unittest discover -v -t src -s src/tests
python3 -m venv build/venv/test-python-3.8
build/venv/test-python-3.8/bin/pip -q --no-cache-dir --disable-pip-version-check install --progress-bar off --upgrade pip setuptools wheel
build/venv/test-python-3.8/bin/pip --no-cache-dir --disable-pip-version-check install --progress-bar off  -e . -e .[tests]
touch build/venv/test-python-3.8.build
build/venv/test-python-3.8/bin/python3 -m unittest discover -v -t src -s src/tests
python3 -m venv build/venv/test-python-3.7
build/venv/test-python-3.7/bin/pip -q --no-cache-dir --disable-pip-version-check install --progress-bar off --upgrade pip setuptools wheel
build/venv/test-python-3.7/bin/pip --no-cache-dir --disable-pip-version-check install --progress-bar off  -e . -e .[tests]
touch build/venv/test-python-3.7.build
build/venv/test-python-3.7/bin/python3 -m unittest discover -v -t src -s src/tests
python3 -m venv build/venv/lint-python-3.9
build/venv/lint-python-3.9/bin/pip -q --no-cache-dir --disable-pip-version-check install --progress-bar off --upgrade pip setuptools wheel
build/venv/lint-python-3.9/bin/pip --no-cache-dir --disable-pip-version-check install --progress-bar off  -e . pylint==2.7.2
touch build/venv/lint-python-3.9.build
build/venv/lint-python-3.9/bin/python3 -m pylint -j 0 setup.py src
python3 -m venv build/venv/doc-python-3.9
build/venv/doc-python-3.9/bin/pip -q --no-cache-dir --disable-pip-version-check install --progress-bar off --upgrade pip setuptools wheel
build/venv/doc-python-3.9/bin/pip --no-cache-dir --disable-pip-version-check install --progress-bar off  -e . sphinx==3.5.1 sphinx_rtd_theme==0.5.1
touch build/venv/doc-python-3.9.build
build/venv/doc-python-3.9/bin/sphinx-build -W -a -b doctest -d build/doc/doctrees doc build/doc/doctest
build/venv/doc-python-3.9/bin/sphinx-build -W -a -b html -d build/doc/doctrees doc build/doc/html
python3 -m venv build/venv/cover-python-3.9
build/venv/cover-python-3.9/bin/pip -q --no-cache-dir --disable-pip-version-check install --progress-bar off --upgrade pip setuptools wheel
build/venv/cover-python-3.9/bin/pip --no-cache-dir --disable-pip-version-check install --progress-bar off  -e . -e .[tests] coverage==5.5
touch build/venv/cover-python-3.9.build
build/venv/cover-python-3.9/bin/python3 -m coverage run --branch --source src -m unittest discover -v -t src -s src/tests
build/venv/cover-python-3.9/bin/python3 -m coverage html -d build/coverage
build/venv/cover-python-3.9/bin/python3 -m coverage report --fail-under 100
'''
            )

    def test_commit_overrides(self):
        test_files = create_test_files([
            (
                'Makefile',
                '''\
PYTHON_VERSIONS := \
    3.9 \
    3.8 \
    3.7

SPHINX_DOC := doc

include Makefile.base
'''
            ),
            ('Makefile.base', MAKEFILE_BASE)
        ])
        with test_files as test_dir:
            # Check make commit commands
            self.assert_make_output(
                self.check_output(
                    ['make', 'commit', '-n'],
                    test_dir,
                    env = {
                        'NO_DOCKER': '',
                        'PIP_ARGS': '--bogus-pip-pargs',
                        'PIP_INSTALL_ARGS': '--bogus-pip-install-args',
                        'COVERAGE_VERSION': 'bogus-coverage-version',
                        'COVERAGE_REPORT_ARGS': '--bogus-coverage-report-args',
                        'PYLINT_VERSION': 'bogus-pylint-version',
                        'PYLINT_ARGS': '--bogus-pylint-args',
                        'SPHINX_VERSION': 'bogus-sphinx-version',
                        'SPHINX_RTD_THEME_VERSION': 'bogus-sphinx-rtd-theme-version',
                        'SPHINX_ARGS': '--bogus-sphinx-args',
                        'SPHINX_DOC': 'bogus-sphinx-doc'
                    }
                ),
                '''\
docker pull -q python:3.9
docker run --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd`  python:3.9 python3 -m venv build/venv/test-python-3.9
docker run --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd`  python:3.9 build/venv/test-python-3.9/bin/pip -q --bogus-pip-pargs install --bogus-pip-install-args --upgrade pip setuptools wheel
docker run --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd`  python:3.9 build/venv/test-python-3.9/bin/pip --bogus-pip-pargs install --bogus-pip-install-args  -e . -e .[tests]
touch build/venv/test-python-3.9.build
docker run --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd`  python:3.9 build/venv/test-python-3.9/bin/python3 -m unittest discover -v -t src -s src/tests
docker pull -q python:3.8
docker run --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd`  python:3.8 python3 -m venv build/venv/test-python-3.8
docker run --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd`  python:3.8 build/venv/test-python-3.8/bin/pip -q --bogus-pip-pargs install --bogus-pip-install-args --upgrade pip setuptools wheel
docker run --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd`  python:3.8 build/venv/test-python-3.8/bin/pip --bogus-pip-pargs install --bogus-pip-install-args  -e . -e .[tests]
touch build/venv/test-python-3.8.build
docker run --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd`  python:3.8 build/venv/test-python-3.8/bin/python3 -m unittest discover -v -t src -s src/tests
docker pull -q python:3.7
docker run --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd`  python:3.7 python3 -m venv build/venv/test-python-3.7
docker run --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd`  python:3.7 build/venv/test-python-3.7/bin/pip -q --bogus-pip-pargs install --bogus-pip-install-args --upgrade pip setuptools wheel
docker run --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd`  python:3.7 build/venv/test-python-3.7/bin/pip --bogus-pip-pargs install --bogus-pip-install-args  -e . -e .[tests]
touch build/venv/test-python-3.7.build
docker run --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd`  python:3.7 build/venv/test-python-3.7/bin/python3 -m unittest discover -v -t src -s src/tests
docker pull -q python:3.9
docker run --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd`  python:3.9 python3 -m venv build/venv/lint-python-3.9
docker run --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd`  python:3.9 build/venv/lint-python-3.9/bin/pip -q --bogus-pip-pargs install --bogus-pip-install-args --upgrade pip setuptools wheel
docker run --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd`  python:3.9 build/venv/lint-python-3.9/bin/pip --bogus-pip-pargs install --bogus-pip-install-args  -e . pylint==bogus-pylint-version
touch build/venv/lint-python-3.9.build
docker run --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd`  python:3.9 build/venv/lint-python-3.9/bin/python3 -m pylint --bogus-pylint-args setup.py src
docker pull -q python:3.9
docker run --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd`  python:3.9 python3 -m venv build/venv/doc-python-3.9
docker run --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd`  python:3.9 build/venv/doc-python-3.9/bin/pip -q --bogus-pip-pargs install --bogus-pip-install-args --upgrade pip setuptools wheel
docker run --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd`  python:3.9 build/venv/doc-python-3.9/bin/pip --bogus-pip-pargs install --bogus-pip-install-args  -e . sphinx==bogus-sphinx-version sphinx_rtd_theme==bogus-sphinx-rtd-theme-version
touch build/venv/doc-python-3.9.build
docker run --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd`  python:3.9 build/venv/doc-python-3.9/bin/sphinx-build --bogus-sphinx-args -b doctest -d build/doc/doctrees doc build/doc/doctest
docker run --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd`  python:3.9 build/venv/doc-python-3.9/bin/sphinx-build --bogus-sphinx-args -b html -d build/doc/doctrees doc build/doc/html
docker pull -q python:3.9
docker run --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd`  python:3.9 python3 -m venv build/venv/cover-python-3.9
docker run --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd`  python:3.9 build/venv/cover-python-3.9/bin/pip -q --bogus-pip-pargs install --bogus-pip-install-args --upgrade pip setuptools wheel
docker run --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd`  python:3.9 build/venv/cover-python-3.9/bin/pip --bogus-pip-pargs install --bogus-pip-install-args  -e . -e .[tests] coverage==bogus-coverage-version
touch build/venv/cover-python-3.9.build
docker run --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd`  python:3.9 build/venv/cover-python-3.9/bin/python3 -m coverage run --branch --source src -m unittest discover -v -t src -s src/tests
docker run --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd`  python:3.9 build/venv/cover-python-3.9/bin/python3 -m coverage html -d build/coverage
docker run --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd`  python:3.9 build/venv/cover-python-3.9/bin/python3 -m coverage report --bogus-coverage-report-args
'''
            )

    def test_twine(self):
        test_files = create_test_files([
            ('Makefile', DEFAULT_MAKEFILE),
            ('Makefile.base', MAKEFILE_BASE)
        ])
        with test_files as test_dir:
            # Touch the environment build sentinels
            os.makedirs(os.path.join(test_dir, 'build', 'venv'))
            Path(os.path.join(test_dir, 'build', 'venv', 'cover-python-3.9.build')).touch()
            Path(os.path.join(test_dir, 'build', 'venv', 'doc-python-3.9.build')).touch()
            Path(os.path.join(test_dir, 'build', 'venv', 'lint-python-3.9.build')).touch()
            Path(os.path.join(test_dir, 'build', 'venv', 'test-python-3.9.build')).touch()
            Path(os.path.join(test_dir, 'build', 'venv', 'test-python-3.8.build')).touch()
            Path(os.path.join(test_dir, 'build', 'venv', 'test-python-3.7.build')).touch()

            # Check make twine commands
            self.assert_make_output(
                self.check_output(['make', 'twine', '-n'], test_dir),
                '''\
docker run --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd`  python:3.9 build/venv/test-python-3.9/bin/python3 -m unittest discover -v -t src -s src/tests
docker run --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd`  python:3.8 build/venv/test-python-3.8/bin/python3 -m unittest discover -v -t src -s src/tests
docker run --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd`  python:3.7 build/venv/test-python-3.7/bin/python3 -m unittest discover -v -t src -s src/tests
docker run --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd`  python:3.9 build/venv/lint-python-3.9/bin/python3 -m pylint -j 0 setup.py src
docker run --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd`  python:3.9 build/venv/doc-python-3.9/bin/sphinx-build -W -a -b doctest -d build/doc/doctrees doc build/doc/doctest
docker run --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd`  python:3.9 build/venv/doc-python-3.9/bin/sphinx-build -W -a -b html -d build/doc/doctrees doc build/doc/html
docker run --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd`  python:3.9 build/venv/cover-python-3.9/bin/python3 -m coverage run --branch --source src -m unittest discover -v -t src -s src/tests
docker run --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd`  python:3.9 build/venv/cover-python-3.9/bin/python3 -m coverage html -d build/coverage
docker run --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd`  python:3.9 build/venv/cover-python-3.9/bin/python3 -m coverage report --fail-under 100
docker pull -q python:3.9
docker run --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd`  -i python:3.9 python3 -m venv build/venv/twine-python-3.9
docker run --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd`  -i python:3.9 build/venv/twine-python-3.9/bin/pip -q --no-cache-dir --disable-pip-version-check install --progress-bar off --upgrade pip setuptools wheel
docker run --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd`  -i python:3.9 build/venv/twine-python-3.9/bin/pip --no-cache-dir --disable-pip-version-check install --progress-bar off  -e . twine
touch build/venv/twine-python-3.9.build
docker run --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd`  -i python:3.9 build/venv/twine-python-3.9/bin/python3 setup.py sdist
docker run --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd`  -i python:3.9 build/venv/twine-python-3.9/bin/twine check dist/*.tar.gz
docker run --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd`  -i python:3.9 build/venv/twine-python-3.9/bin/twine upload dist/*.tar.gz
'''
            )

            # Touch the environment build sentinels
            Path(os.path.join(test_dir, 'build', 'venv', 'twine-python-3.9.build')).touch()

            # Check subsequent make twine commands
            self.assert_make_output(
                self.check_output(['make', 'twine', '-n'], test_dir),
                '''\
docker run --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd`  python:3.9 build/venv/test-python-3.9/bin/python3 -m unittest discover -v -t src -s src/tests
docker run --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd`  python:3.8 build/venv/test-python-3.8/bin/python3 -m unittest discover -v -t src -s src/tests
docker run --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd`  python:3.7 build/venv/test-python-3.7/bin/python3 -m unittest discover -v -t src -s src/tests
docker run --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd`  python:3.9 build/venv/lint-python-3.9/bin/python3 -m pylint -j 0 setup.py src
docker run --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd`  python:3.9 build/venv/doc-python-3.9/bin/sphinx-build -W -a -b doctest -d build/doc/doctrees doc build/doc/doctest
docker run --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd`  python:3.9 build/venv/doc-python-3.9/bin/sphinx-build -W -a -b html -d build/doc/doctrees doc build/doc/html
docker run --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd`  python:3.9 build/venv/cover-python-3.9/bin/python3 -m coverage run --branch --source src -m unittest discover -v -t src -s src/tests
docker run --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd`  python:3.9 build/venv/cover-python-3.9/bin/python3 -m coverage html -d build/coverage
docker run --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd`  python:3.9 build/venv/cover-python-3.9/bin/python3 -m coverage report --fail-under 100
docker run --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd`  -i python:3.9 build/venv/twine-python-3.9/bin/python3 setup.py sdist
docker run --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd`  -i python:3.9 build/venv/twine-python-3.9/bin/twine check dist/*.tar.gz
docker run --rm -u `id -g`:`id -g` -v `pwd`:`pwd` -w `pwd`  -i python:3.9 build/venv/twine-python-3.9/bin/twine upload dist/*.tar.gz
'''
            )
