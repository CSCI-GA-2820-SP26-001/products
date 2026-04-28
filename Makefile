# These can be overidden with env vars.
REGISTRY ?= cluster-registry:5000
IMAGE_NAME ?= products
IMAGE_TAG ?= 1.0
IMAGE ?= $(REGISTRY)/$(IMAGE_NAME):$(IMAGE_TAG)
POSTGRES_IMAGE ?= postgres:15
PLATFORM ?= "linux/amd64,linux/arm64"
CLUSTER ?= nyu-devops

.SILENT:

.PHONY: help
help: ## Display this help.
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_0-9-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

.PHONY: all
all: help

##@ Development

.PHONY: clean
clean:	## Removes all dangling build cache
	$(info Removing all dangling build cache..)
	-docker rmi $(IMAGE)
	docker image prune -f
	docker buildx prune -f

.PHONY: install
install: ## Install Python dependencies
	$(info Installing dependencies...)
	sudo pipenv install --system --dev

.PHONY: lint
lint: ## Run the linter
	$(info Running linting...)
	-flake8 service tests --count --select=E9,F63,F7,F82 --show-source --statistics
	-flake8 service tests --count --max-complexity=10 --max-line-length=127 --statistics
	-pylint service tests --max-line-length=127

.PHONY: test
test: ## Run the unit tests
	$(info Running tests...)
	export DATABASE_URI=sqlite:///test.db; export RETRY_COUNT=1; pytest --pspec --cov=service --cov-fail-under=95 --disable-warnings

.PHONY: bdd
bdd: ## Run BDD tests with Behave (requires the service running on $$BASE_URL)
	$(info Running BDD tests with Behave + Selenium...)
	behave

.PHONY: run
run: ## Run the service
	$(info Starting service...)
	honcho start

.PHONY: secret
secret: ## Generate a secret hex key
	$(info Generating a new secret key...)
	python3 -c 'import secrets; print(secrets.token_hex())'

##@ Kubernetes

.PHONY: cluster
cluster: ## Create a K3D Kubernetes cluster with load balancer and registry
	$(info Creating Kubernetes cluster $(CLUSTER) with a registry and 2 worker nodes...)
	k3d cluster create --config k3d-config.yaml

.PHONY: preflight
preflight: ## Verify local machine is configured to push to cluster-registry:5000
	$(info Checking local preflight requirements...)
	@getent hosts cluster-registry >/dev/null 2>&1 || { \
		echo "ERROR: hostname 'cluster-registry' does not resolve locally."; \
		echo "       Add this line to /etc/hosts (needs sudo):"; \
		echo "         127.0.0.1 cluster-registry"; \
		exit 1; \
	}
	@docker info 2>/dev/null | grep -q 'cluster-registry:5000' || { \
		echo "ERROR: docker daemon is missing cluster-registry:5000 from insecure-registries."; \
		echo "       Write /etc/docker/daemon.json (needs sudo):"; \
		echo "         {\"insecure-registries\": [\"cluster-registry:5000\"]}"; \
		echo "       Then: sudo systemctl restart docker   (or restart Docker Desktop)"; \
		exit 1; \
	}
	@echo "Preflight OK: cluster-registry resolves and docker treats it as insecure."

.PHONY: cluster-rm
cluster-rm: ## Remove a K3D Kubernetes cluster
	$(info Removing Kubernetes cluster...)
	k3d cluster delete nyu-devops

.PHONY: seed-postgres
seed-postgres: preflight ## Mirror the postgres image into the local cluster-registry
	$(info Seeding $(POSTGRES_IMAGE) into $(REGISTRY)...)
	docker pull $(POSTGRES_IMAGE)
	docker tag $(POSTGRES_IMAGE) $(REGISTRY)/$(POSTGRES_IMAGE)
	docker push $(REGISTRY)/$(POSTGRES_IMAGE)

.PHONY: deploy
deploy: ## Deploy the service on local Kubernetes
	$(info Deploying service locally...)
	kubectl apply -R -f k8s/

############################################################
# COMMANDS FOR BUILDING THE IMAGE
############################################################

##@ Image Build and Push

.PHONY: init
init: export DOCKER_BUILDKIT=1
init:	## Creates the buildx instance
	$(info Initializing Builder...)
	-docker buildx create --use --name=qemu
	docker buildx inspect --bootstrap

.PHONY: build
build:	## Build the project container image for local platform
	$(info Building $(IMAGE)...)
	docker build --rm --pull --tag $(IMAGE) .

.PHONY: push
push: preflight	## Push the image to the container registry
	$(info Pushing $(IMAGE)...)
	docker push $(IMAGE)

.PHONY: buildx
buildx:	## Build multi-platform image with buildx
	$(info Building multi-platform image $(IMAGE) for $(PLATFORM)...)
	docker buildx build --file Dockerfile --pull --platform=$(PLATFORM) --tag $(IMAGE) --push .

.PHONY: remove
remove:	## Stop and remove the buildx builder
	$(info Stopping and removing the builder image...)
	docker buildx stop
	docker buildx rm
