# -*- makefile-gmake -*-
# Licensed under the MIT License
# https://github.com/craigahobbs/python-build/blob/main/LICENSE

.DEFAULT_GOAL := help


# Python image
PYTHON_IMAGE ?= python:3
ifneq '$(USE_DOCKER)' ''
PYTHON_RUN := docker run -i --rm -u `id -g`:`id -g` -v $(HOME):$(HOME) -v `pwd`:`pwd` -w `pwd` -e HOME=$(HOME)$(if $(DOCKER_ENV), $(DOCKER_ENV)) $(PYTHON_IMAGE)
else ifneq '$(USE_PODMAN)' ''
PYTHON_RUN := podman run -i --rm -v $(HOME):$(HOME) -v `pwd`:`pwd` -w `pwd` -e HOME=$(HOME)$(if $(DOCKER_ENV), $(DOCKER_ENV)) $(PYTHON_IMAGE)
endif

# Python pip option
PIP_ARGS ?= -q --disable-pip-version-check
PIP_INSTALL_ARGS ?= --progress-bar off --no-compile

# Python virtual environment
DEFAULT_VENV_DIR := build/env
DEFAULT_VENV_BIN := $(strip $(PYTHON_RUN) $(DEFAULT_VENV_DIR)/bin)
DEFAULT_VENV_PYTHON := $(strip $(PYTHON_RUN) $(DEFAULT_VENV_DIR)/bin/python3)
DEFAULT_VENV_BUILD := $(DEFAULT_VENV_DIR).build
ifeq '$(USE_DOCKER)$(USE_PODMAN)' ''
ifeq '$(OS)' 'Windows_NT'
ifeq ($(shell python3 -c "import sysconfig; print(sysconfig.get_preferred_scheme('user'))"),nt_user)
DEFAULT_VENV_BIN := $(strip $(PYTHON_RUN) $(DEFAULT_VENV_DIR)/Scripts)
DEFAULT_VENV_PYTHON := $(strip $(PYTHON_RUN) $(DEFAULT_VENV_DIR)/Scripts/python.exe)
endif
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
ifneq '$(USE_DOCKER)' ''
	-docker rmi -f $(PYTHON_IMAGE)
else ifneq '$(USE_PODMAN)' ''
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
	$(PYTHON_RUN) python3 -m venv --without-pip $(DEFAULT_VENV_DIR)
	$(PYTHON_RUN) python3 -m pip --python $(DEFAULT_VENV_DIR) $(PIP_ARGS) install $(PIP_INSTALL_ARGS) $(TESTS_REQUIRE)
	touch $@
