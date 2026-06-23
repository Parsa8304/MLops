# Common commands for the Intent Classifier project.
# Run `make help` to see what is available.

PYTHON ?= python3
PORT ?= 6000
IMAGE ?= intent-classifier

.PHONY: help setup train run test docker-build docker-run clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'

setup: ## Create a virtualenv and install dependencies
	$(PYTHON) -m venv .venv
	. .venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt

train: ## Train the model and write the artifact
	$(PYTHON) model/train.py

run: ## Run the API locally (http://127.0.0.1:$(PORT))
	$(PYTHON) app.py

test: ## Run the test suite
	$(PYTHON) -m pytest -q

docker-build: ## Build the Docker image
	docker build -t $(IMAGE) .

docker-run: ## Run the Docker image on port $(PORT)
	docker run --rm -p $(PORT):6000 $(IMAGE)

clean: ## Remove caches and the model artifact
	rm -rf model/artifacts __pycache__ */__pycache__ .pytest_cache
