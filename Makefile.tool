# -*- makefile-gmake -*-
# Licensed under the MIT License
# https://github.com/craigahobbs/python-build/blob/main/LICENSE

.DEFAULT_GOAL := help


# Python image
PYTHON_IMAGE ?= python:3
ifneq '$(USE_PODMAN)' ''
PYTHON_RUN := podman run -i --rm -v $$HOME:$$HOME -v `pwd`:`pwd` -w `pwd` -e HOME=$$HOME $(PYTHON_IMAGE)
endif


# Python virtual environment
DEFAULT_VENV_BIN := $(PYTHON_RUN) build/env/bin
DEFAULT_VENV_PYTHON := $(PYTHON_RUN) build/env/bin/python3
DEFAULT_VENV_BUILD := build/env.build
ifeq '$(OS)' 'Windows_NT'
ifeq ($(shell python3 -c "import sysconfig; print(sysconfig.get_preferred_scheme('user'))"),nt_user)
DEFAULT_VENV_BIN := $(PYTHON_RUN) build/env/Scripts
DEFAULT_VENV_PYTHON := $(PYTHON_RUN) build/env/Scripts/python.exe
endif
endif


.PHONY: _help help
help: _help
_help:
	@echo "usage: make [clean|commit|gh-pages|lint|test|superclean]"


.PHONY: _clean clean
clean: _clean
_clean:
	rm -rf build/


.PHONY: _superclean superclean
superclean: clean _superclean
_superclean:
ifneq '$(USE_PODMAN)' ''
	-podman rmi -f $(PYTHON_IMAGE)
endif


.PHONY: commit
commit: test lint


.PHONY: test
test:


.PHONY: lint
lint:


.PHONY: gh-pages
gh-pages:


$(DEFAULT_VENV_BUILD):
	mkdir -p build
	$(PYTHON_RUN) python3 -m venv --upgrade-deps build/env
	$(DEFAULT_VENV_BIN)/pip install $(TESTS_REQUIRE)
	touch $@
