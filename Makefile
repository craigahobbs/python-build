# Licensed under the MIT License
# https://github.com/craigahobbs/python-build/blob/main/LICENSE


.PHONY: help
help:
	@echo 'usage: make [changelog|clean|commit|superclean|test]'


.PHONY: commit
commit: test


.PHONY: clean
clean:
	rm -rf build/ test-actual/


.PHONY: gh-pages
gh-pages:


.PHONY: superclean
superclean: clean


.PHONY: test
test:
	rm -rf test-actual/
	@echo Tests completed - all passed


# Test rule function - name, make args
define TEST_RULE
.PHONY: test-$(strip $(1))
test-$(strip $(1)):
	@echo 'Testing "$(strip $(1))"...'
	mkdir -p test-actual/
	$(MAKE) -C tests/$(strip $(1))/ -n --no-print-directory$(if $(strip $(2)), $(strip $(2))) \
		| sed -E "s/^(make\[)[0-9]+(\].*: Nothing to be done for )[\`']/\1X\2'/" \
		> test-actual/$(strip $(1)).txt
	diff test-actual/$(strip $(1)).txt test-expected/$(strip $(1)).txt
	rm test-actual/$(strip $(1)).txt

test: test-$(strip $(1))
endef


# Use podman by default
export USE_PODMAN=1


# Don't test anything OS-specific
OS := Unknown


# Tests
$(eval $(call TEST_RULE, changelog, changelog))
$(eval $(call TEST_RULE, clean, clean))
$(eval $(call TEST_RULE, commit, commit))
$(eval $(call TEST_RULE, commit-no-podman, commit USE_PODMAN=))
$(eval $(call TEST_RULE, commit-overrides, commit \
  PIP_ARGS='--bogus-pip-arg' \
  PIP_INSTALL_ARGS='--bogus-pip-install-arg' \
  UNITTEST_ARGS='--bogus-unittest-args' \
  COVERAGE_VERSION='bogus-coverage-version' \
  COVERAGE_ARGS='--bogus-coverage-arg' \
  COVERAGE_REPORT_ARGS='--bogus-coverage-report-arg' \
  PYLINT_VERSION='bogus-pylint-version' \
  PYLINT_ARGS='--bogus-pylint-arg' \
  SPHINX_VERSION='bogus-sphinx-version' \
  SPHINX_ARGS='--bogus-sphinx-arg' \
  SPHINX_DOC='bogus-sphinx-doc' \
  TESTS_REQUIRE='"foobar >= 1.0"' \
))
$(eval $(call TEST_RULE, commit-overrides-unittest-parallel, commit \
  UNITTEST_PARALLEL_VERSION='bogus-unittest-parallel-version' \
  UNITTEST_PARALLEL_ARGS='--bogus-unittest-parallel-arg' \
  UNITTEST_PARALLEL_COVERAGE_ARGS='--bogus-unittest-parallel-coverage-arg' \
))
$(eval $(call TEST_RULE, cover, cover))
$(eval $(call TEST_RULE, cover-2, cover))
$(eval $(call TEST_RULE, cover-test, cover TEST=tests.test_package))
$(eval $(call TEST_RULE, cover-unittest-parallel, cover))
$(eval $(call TEST_RULE, doc, doc))
$(eval $(call TEST_RULE, doc-2, doc))
$(eval $(call TEST_RULE, doc-none, doc))
$(eval $(call TEST_RULE, gh-pages, gh-pages))
$(eval $(call TEST_RULE, help))
$(eval $(call TEST_RULE, lint, lint))
$(eval $(call TEST_RULE, lint-2, lint))
$(eval $(call TEST_RULE, publish, publish))
$(eval $(call TEST_RULE, publish-2, publish))
$(eval $(call TEST_RULE, superclean, superclean))
$(eval $(call TEST_RULE, test, test))
$(eval $(call TEST_RULE, test-2, test))
$(eval $(call TEST_RULE, test-exclude, test))
$(eval $(call TEST_RULE, test-test, test TEST=tests.test_package))
$(eval $(call TEST_RULE, test-unittest-parallel, test))
$(eval $(call TEST_RULE, test-unittest-parallel-2, test))


.PHONY: changelog
changelog: build/venv.build
	build/venv/$(VENV_BIN)/simple-git-changelog


build/venv.build:
	python3 -m venv --upgrade-deps build/venv
	build/venv/$(VENV_BIN)/pip -q install --progress-bar off simple-git-changelog
	touch $@


# Windows support
VENV_BIN := bin
ifeq '$(OS)' 'Windows_NT'
ifeq ($(shell python3 -c "import sysconfig; print(sysconfig.get_preferred_scheme('user'))"),nt_user)
VENV_BIN := Scripts
endif
endif
