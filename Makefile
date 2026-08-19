NAME := pytest_localstack

INSTALL_STAMP := .install.stamp
POETRY := $(shell command -v poetry 2> /dev/null)


.DEFAULT_GOAL := help

.PHONY: help
help:  ## print this help
	@# https://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'


.PHONY: install  ## create development virtualenv
install: $(INSTALL_STAMP)
$(INSTALL_STAMP): pyproject.toml poetry.lock
	@if [ -z $(POETRY) ]; then echo "Poetry could not be found. See https://python-poetry.org/docs/"; exit 2; fi
	$(POETRY) install
	@touch $(INSTALL_STAMP)

.PHONY: clean
clean: ## remove all build, test, coverage and Python artifacts
	rm -rf \
		$(INSTALL_STAMP) \
		.coverage \
		.mypy_cache \
		.venv/ \
		build/ \
		dist/ \
		.eggs/ \
		.tox/ \
		.coverage \
		htmlcov/ \
		coverage.xml \
		junit.xml \
		junit-*.xml
	find . \( \
		-name "*.egg-info" \
		-o -name "*.egg" \
		-o -name "*.pyc" \
		-o -name "*.pyo" \
		-o -name "*~" \
		-o -name "__pycache__" \
		\) \
		-exec rm -fr {} +

.PHONY: lint
lint: $(INSTALL_STAMP)  ## check code style
	$(POETRY) run isort --check-only ./tests/ $(NAME)
	$(POETRY) run black --check ./tests/ $(NAME) --diff
	$(POETRY) run flake8 ./tests/ $(NAME)
	$(POETRY) run mypy ./tests/ $(NAME) --ignore-missing-imports
	$(POETRY) run bandit -r $(NAME) -s B608

.PHONY: fmt
fmt: $(INSTALL_STAMP)  ## apply code style formatting
	$(POETRY) run isort --profile=black --lines-after-imports=2 ./tests/ $(NAME)
	$(POETRY) run black ./tests/ $(NAME)

.PHONY: test
test: $(INSTALL_STAMP)  ## run all tests
	$(POETRY) run pytest

.PHONY: test-unit
test-unit: $(INSTALL_STAMP)  ## run unit tests with coverage
	$(POETRY) run pytest tests/unit -ra --cov=$(NAME) -n auto

.PHONY: test-integration
test-integration: $(INSTALL_STAMP)  ## run integration tests with coverage (appended)
	$(POETRY) run pytest tests/integration -ra --cov=$(NAME) --cov-append -n auto

.PHONY: test-functional
test-functional: $(INSTALL_STAMP)  ## run functional tests with coverage (requires Docker)
	$(POETRY) run pytest tests/functional -ra --cov=$(NAME)

.PHONY: coverage-report
coverage-report: $(INSTALL_STAMP)  ## generate coverage.xml and htmlcov/ from collected coverage
	$(POETRY) run coverage xml
	$(POETRY) run coverage html

.PHONY: docs
docs: $(INSTALL_STAMP)  ## build documentation
	$(POETRY) run $(MAKE) -C docs html


.PHONY: docs-live
docs-live: $(INSTALL_STAMP)  ## build and view docs in real-time
	$(POETRY) run sphinx-autobuild -b html \
		-p 0 \
		--open-browser \
		--watch ./ \
		--ignore ".git/*" \
		--ignore ".venv/*" \
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
