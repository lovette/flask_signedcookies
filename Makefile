VENVNAME := $(shell basename $(CURDIR))
VENVROOT := ${HOME}/.virtualenvs
VENVDIR := ${VENVROOT}/${VENVNAME}

ERROR_NO_VIRTUALENV = $(error Python virtualenv is not active, activate first)
ERROR_ACTIVE_VIRTUALENV = $(error Python virtualenv is active, deactivate first)

############################
## Help

.PHONY: help
.DEFAULT_GOAL := help
help:
	@printf 'Usage: make [VARIABLE=] TARGET\n'
	@awk 'BEGIN {FS = ":.*##";} /^[a-zA-Z1-9_-]+:.*?##/ { printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)


############################
##@ Python virtualenv

.PHONY: virtualenv
virtualenv:  ## Create venv directory and install pip
ifdef VIRTUAL_ENV
	$(ERROR_ACTIVE_VIRTUALENV)
endif
	python3 -m venv --prompt ${VENVNAME} ${VENVDIR}
	${VENVDIR}/bin/python3 -m pip install --require-virtualenv --upgrade --no-cache-dir -r requirements-venv.txt
	@echo
	@echo "EMPTY Python virtualenv named '${VENVNAME}' created in ${VENVROOT}"
	@echo "To activate: source ${VENVDIR}/bin/activate"
	@echo "To install packages: 'make install' or 'make install-dev'"

.PHONY: rmvirtualenv
rmvirtualenv:  ## Remove venv and Python cache directories
ifdef VIRTUAL_ENV
	$(ERROR_ACTIVE_VIRTUALENV)
endif
	rm -rf ${VENVDIR}
	find . -type d -name __pycache__ -print -exec rm -rf {} +


############################
##@ Python install

.PHONY: install
install:  ## Install project packages and script
	python3 -m pip install --require-virtualenv --upgrade -r requirements.txt .

.PHONY: install-dev
install-dev:  ## Install project packages and script for development
	python3 -m pip install --require-virtualenv --upgrade -r requirements.txt -r requirements-dev.txt -e .


############################
##@ Python requirements

requirements.txt: pyproject.toml
ifndef VIRTUAL_ENV
	$(ERROR_NO_VIRTUALENV)
endif
	python3 -m piptools compile --upgrade --strip-extras --resolver=backtracking --quiet -o requirements.txt pyproject.toml

requirements-dev.txt: requirements.txt
ifndef VIRTUAL_ENV
	$(ERROR_NO_VIRTUALENV)
endif
	python3 -m piptools compile --upgrade --strip-extras --resolver=backtracking --quiet --extra dev --constraint requirements.txt -o requirements-dev.txt pyproject.toml

.PHONY: requirements
requirements: requirements-dev.txt  ## Generate requirements[-dev].txt based on `pyproject.toml` dependencies.

############################
##@ Python Ruff

.PHONY: ruffcheck
ruffcheck:  ## Run Ruff on project files
ifndef VIRTUAL_ENV
	$(ERROR_NO_VIRTUALENV)
endif
	ruff check src

.PHONY: ruffclean
ruffclean:  ## Clear Ruff caches
ifndef VIRTUAL_ENV
	$(ERROR_NO_VIRTUALENV)
endif
	ruff clean


############################
##@ Build

.PHONY: distbuild
distbuild:  ## Build package
ifndef VIRTUAL_ENV
	$(ERROR_NO_VIRTUALENV)
endif
	python -m build

.PHONY: distclean
distclean:  ## Delete build files, python cache and package build artifacts
	rm -f requirements.txt requirements-dev.txt
	rm -rf build dist .ruff_cache
	find . -type d -name __pycache__ -print -exec rm -rf {} +
	find . -type d -name '*.egg-info' -print -exec rm -rf {} +
	find . -type f -name '*.pyc' -delete
