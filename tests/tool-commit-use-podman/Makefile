PYTHON_IMAGE := python:3.X
TESTS_REQUIRE := bogus-tool
HOME := /bogus-home

include ../../Makefile.tool

test: $(DEFAULT_VENV_BUILD)
	$(DEFAULT_VENV_BIN)/bogus-tool test

lint: $(DEFAULT_VENV_BUILD)
	$(DEFAULT_VENV_BIN)/bogus-tool lint
