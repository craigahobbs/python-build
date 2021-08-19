# Licensed under the MIT License
# https://github.com/craigahobbs/python-build/blob/main/LICENSE


PYLINT_VERSION ?= 2.9.*


.PHONY: help
help:
	@echo 'usage: make [changelog|clean|commit|lint|superclean|test]'


.PHONY: commit
commit: test lint


.PHONY: clean
clean:
	rm -rf __pycache__/ build/


.PHONY: superclean
superclean: clean


.PHONY: test
test:
	python3 -m unittest -v tests.py


.PHONY: lint
lint: build/venv.build
	build/venv/bin/pylint tests.py


.PHONY: changelog
changelog: build/venv.build
	build/venv/bin/simple-git-changelog


build/venv.build:
	python3 -m venv build/venv
	build/venv/bin/pip --disable-pip-version-check --no-cache-dir install --progress-bar off -U pip setuptools wheel
	build/venv/bin/pip --disable-pip-version-check --no-cache-dir install --progress-bar off \
		pylint=="$(PYLINT_VERSION)" simple-git-changelog
	touch $@
