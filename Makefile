VIRTUALENV := $(shell python -c 'from __future__ import print_function; import sys; print(sys.prefix if hasattr(sys, "real_prefix") or (hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix) else "", end="")')
ifeq ($(VIRTUALENV),)
VIRTUALENV := .venv
endif

PIPENV_VARS := PIPENV_VENV_IN_PROJECT=1
PIPENV := $(PIPENV_VARS) pipenv
PIPENV_RUN := $(PIPENV) run



help:  ## print this help
	@# https://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'


env: $(VIRTUALENV)  ## create development virtualenv
.PHONY: env
$(VIRTUALENV): $(VIRTUALENV)/bin/activate
$(VIRTUALENV)/bin/activate: Pipfile.lock
	$(PIPENV) install --dev --deploy
	touch $(VIRTUALENV)/bin/activate
Pipfile.lock: Pipfile setup.py
	$(PIPENV) lock


test: $(VIRTUALENV)  ## run tests
	$(PIPENV_RUN) pytest
.PHONY: ftest


lint: $(VIRTUALENV)  ## check code style
	$(PIPENV) check
	$(PIPENV_RUN) flake8
	$(PIPENV_RUN) flake8 --config tests/.flake8 tests/
	@if $(PIPENV_RUN) python setup.py check --restructuredtext --strict; then\
		echo ".rst files OK"; \
	else \
		echo ".rst files ERROR"; \
	fi
.PHONY: lint


isort: $(VIRTUALENV)  ## sort import statements
	$(PIPENV_RUN) isort
.PHONY: isort


docs: $(VIRTUALENV)
	$(PIPENV_RUN) $(MAKE) -C docs html
.PHONY: docs


docs-live: $(VIRTUALENV)  ## build and view docs in real-time
	$(PIPENV_RUN) sphinx-autobuild -b html \
		-p 0 \
		--open-browser \
		--watch docs/ \
		--watch pytest_localstack/ \
		--ignore "*.swp" \
		--ignore "*.pdf" \
		--ignore "*.log" \
		--ignore "*.out" \
		--ignore "*.toc" \
		--ignore "*.aux" \
		--ignore "*.idx" \
		--ignore "*.ind" \
		--ignore "*.ilg" \
		--ignore "*.tex" \
		--ignore "Makefile" \
		--ignore "setup.py" \
		--ignore "setup.cfg" \
		--ignore "Pipfile*" \
		docs docs/_build/html
.PHONY: docs-live


lock: $(VIRTUALENV)  ## regenerate Pipfile.lock file
	$(PIPENV) lock
.PHONY: lock


clean: clean-build clean-pyc clean-env clean-test  ## remove all build, test, coverage and Python artifacts
.PHONY: clean


clean-build:  ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +
.PHONY: clean-build


clean-pyc:  ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +
.PHONY: clean-pyc


clean-env:  ## remove development virtualenv
	pipenv --rm || true
.PHONY: clean-env


clean-test:  ## remove test and coverage artifacts
	rm -rf .tox/ \
	       .coverage \
	       htmlcov/ \
	       coverage.xml \
	       junit.xml \
	       junit-*.xml
.PHONY: clean-test
