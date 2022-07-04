SHELL := bash
.SHELLFLAGS := -eux -o pipefail -c
.DEFAULT_GOAL := build
.DELETE_ON_ERROR:  # If a recipe to build a file exits with an error, delete the file.
.SUFFIXES:  # Remove the default suffixes which are for compiling C projects.
.NOTPARALLEL:  # Disable use of parallel subprocesses.
MAKEFLAGS += --warn-undefined-variables
MAKEFLAGS += --no-builtin-rules


export COLUMNS ?= 70
seperator ?= $(shell printf %${COLUMNS}s | tr " " "═")

platform := $(shell python -c 'import sys; print(sys.platform)')

PYTHON_VERSION ?= 3

export PIP_DISABLE_PIP_VERSION_CHECK=1
pip-install := ve/bin/pip --no-input install --constraint constraints.txt
pip-check := ve/bin/pip show -q

source_code := src

isort := ve/bin/isort --multi-line=VERTICAL_HANGING_INDENT --trailing-comma --no-sections 

########################################################################################
# Build targets
#
# It is acceptable for other targets to implicitly depend on these targets having been
# run.  I.e., it is ok if "make lint" generates an error before "make" has been run.

.PHONY: build
build: ve development-utilities

ve:
	python$(PYTHON_VERSION) -m venv ve
	$(pip-install) -e .

ve/bin/genbadge:
	$(pip-install) genbadge[coverage]

ve/bin/%:
	# Install development utility "$*"
	$(pip-install) $*

# Utilities we use during development.
.PHONY: development-utilities
development-utilities: ve/bin/black
development-utilities: ve/bin/coverage
development-utilities: ve/bin/flake8
development-utilities: ve/bin/genbadge
development-utilities: ve/bin/isort
development-utilities: ve/bin/mypy
development-utilities: ve/bin/pydocstyle
development-utilities: ve/bin/pyinstaller
development-utilities: ve/bin/pylint
development-utilities: ve/bin/twine
development-utilities: ve/bin/wheel

########################################################################################
# Distribution targets

.PHONY: assert-one-dist
assert-one-dist:
	@if [ $$(find dist -name 'manuel-*.tar.gz' | wc -l) != 1 ]; then \
	    echo There must be one and only one distribution file present.; \
	    exit 1; \
	fi

.PHONY: assert-no-unreleased-changes
assert-no-unreleased-changes:
	@if grep unreleased CHANGES.rst > /dev/null; then \
	    echo There must not be any unreleased changes in CHANGES.rst.; \
	    exit 1; \
	fi

.PHONY: assert-version-in-changelog
assert-version-in-changelog:
	@if ! grep $$(ve/bin/python setup.py --version) CHANGES.rst; then \
	    echo The current version number must be mentioned in CHANGES.rst.; \
	    exit 1; \
	fi

.PHONY: assert-matching-versions
assert-matching-versions:
	# verify that the top-most version in the change log matches what is in setup.py
	@env \
	    CHANGE_LOG_VERSION=$$(grep '^[^ ]\+ (20\d\d-\d\d-\d\d)' CHANGES.rst | head -n 1 | cut -d' ' -f1) \
	    SETUP_VERSION=$$(ve/bin/python setup.py --version) \
	    bash -c 'test $$CHANGE_LOG_VERSION = $$SETUP_VERSION'

.PHONY: assert-no-changes
assert-no-changes:
	@if ! output=$$(git status --porcelain) || [ -n "$$output" ]; then \
	    echo There must not be any ucomitted changes.; \
	    exit 1; \
	fi

.PHONY: dist
dist:
	ve/bin/python setup.py sdist

.PHONY: test-dist
test-dist:
	# check to see if the distribution passes the tests
	rm -rf tmp
	mkdir tmp
	tar xzvf $$(find dist -name 'manuel-*.tar.gz') -C tmp
	cd tmp/manuel-* && make && make check
	rm -rf tmp

.PHONY: upload
upload: assert-one-dist
	ve/bin/twine upload --repository manuel $$(find dist -name 'manuel-*.tar.gz')

.PHONY: badges
badges:
	ve/bin/python bin/genbadge coverage -i coverage.xml -o badges/coverage-badge.svg

.PHONY: release
ifeq '$(shell git rev-parse --abbrev-ref HEAD)' 'master'
release: clean-dist assert-no-unreleased-changes assert-matching-versions \
    assert-version-in-changelog badges dist assert-one-dist test-dist \
    assert-no-changes upload
	# now that a release has happened, tag the current HEAD as that release
	git tag $$(ve/bin/python setup.py --version)
	git push origin
	git push origin --tags
else
release:
	@echo Error: must be on master branch to do a release.; exit 1
endif

########################################################################################
# Test and lint targets

.PHONY: pylint
pylint:
	ve/bin/pylint $(source_code) --output-format=colorized

.PHONY: flake8
flake8:
	ve/bin/flake8 $(source_code)

.PHONY: pydocstyle
pydocstyle:
	ve/bin/pydocstyle $(source_code)

.PHONY: mypy
mypy:
	ve/bin/mypy $(source_code) --strict

.PHONY: black-check
black-check:
	ve/bin/black -S $(source_code) --check

.PHONY: isort-check
isort-check:
	$(isort) $(source_code) --diff --check

.PHONY: lint
lint: black-check isort-check

.PHONY: test
test:
	ve/bin/python setup.py test

.PHONY: coverage
coverage:
	ve/bin/coverage run --branch setup.py test
	ve/bin/coverage xml  # the XML output file is used by the "badges" target
	PYTHONWARNINGS=ignore ve/bin/coverage report --ignore-errors --fail-under=97 --show-missing --skip-empty

.PHONY: check
check: test lint coverage

########################################################################################
# Sorce code formatting targets

.PHONY: black
black:
	ve/bin/black -S $(source_code)

.PHONY: isort
isort:
	$(isort) $(source_code)

########################################################################################
# Cleanup targets

.PHONY: clean-%
clean-%:
	rm -rf $*

.PHONY: clean-pycache
clean-pycache:
	find . -name __pycache__ -delete

.PHONY: clean
clean: clean-ve clean-pycache clean-dist
