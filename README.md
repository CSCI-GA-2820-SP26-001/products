# Products Service

[![CI](https://github.com/CSCI-GA-2820-SP26-001/products/actions/workflows/ci.yml/badge.svg)](https://github.com/CSCI-GA-2820-SP26-001/products/actions)
[![codecov](https://codecov.io/gh/CSCI-GA-2820-SP26-001/products/branch/master/graph/badge.svg)](https://codecov.io/gh/CSCI-GA-2820-SP26-001/products)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Language-Python-blue.svg)](https://python.org/)

A RESTful microservice for managing a product catalog, built with Flask and backed by PostgreSQL. Includes a single-page admin UI, Selenium-based BDD tests, and a Tekton CI/CD pipeline for automated deployment to OpenShift.

## Data Model

| Field       | Type    | Required | Description                        |
|-------------|---------|----------|------------------------------------|
| id          | Integer | auto     | Unique identifier                  |
| name        | String  | yes      | Name of the product                |
| description | String  | no       | Description (default: "")          |
| price       | Decimal | yes      | Price of the product               |
| category    | String  | yes      | Product category                   |
| stock       | Integer | no       | Units in stock (default: 0)        |
| available   | Boolean | no       | Availability flag (default: true)  |

## API Endpoints

| Method   | Endpoint                    | Description                              |
|----------|-----------------------------|------------------------------------------|
| `GET`    | `/`                         | Service info and available paths          |
| `GET`    | `/health`                   | Health check — returns `{"status":"OK"}`  |
| `POST`   | `/products`                 | Create a new product                     |
| `GET`    | `/products/{id}`            | Retrieve a product by ID                 |
| `PUT`    | `/products/{id}`            | Update a product                         |
| `DELETE` | `/products/{id}`            | Delete a product                         |
| `GET`    | `/products`                 | List all products (with optional filters)|
| `PUT`    | `/products/{id}/purchase`   | Purchase one unit (decrements stock)     |

### Query Filters on `GET /products`

| Parameter       | Description                                           |
|-----------------|-------------------------------------------------------|
| `name`          | Exact match by product name                           |
| `category`      | Case-insensitive match by category                    |
| `available`     | Filter by availability (`true` or `false`)            |
| `minimum_price` | Minimum price (inclusive)                              |
| `maximum_price` | Maximum price (inclusive)                              |

Examples: `GET /products?category=Electronics`, `GET /products?minimum_price=10&maximum_price=50`

## Admin UI

A set of lightweight admin pages for managing products through the browser:

| Page                          | URL                              |
|-------------------------------|----------------------------------|
| Create a product              | `/admin/products/create`         |
| Read a product by ID          | `/admin/products/read`           |
| Update a product              | `/admin/products/update`         |
| Delete a product              | `/admin/products/delete`         |
| List / Query products         | `/admin/products/list`           |
| Purchase a product            | `/admin/products/purchase`       |

## Running Locally

```bash
make run
```

The service starts at `http://localhost:8080`.

## Testing

### Unit Tests (TDD)

```bash
make test
```

Runs pytest with a minimum coverage threshold of 95%.

### Linting

```bash
make lint
```

Runs flake8 and pylint.

### BDD Tests

The BDD suite uses Behave and Selenium (headless Chrome). Every step interacts through the admin UI — no direct API calls.

```bash
make run          # start the service in one terminal
behave            # run BDD tests in another terminal
```

| Env var        | Default                 | Description                      |
|----------------|-------------------------|----------------------------------|
| `BASE_URL`     | `http://localhost:8080`  | URL of the running service       |
| `WAIT_SECONDS` | `30`                    | Selenium wait timeout in seconds |

Feature files cover Create, Read, Update, Delete, List, Query (category filter), and Purchase (action) — 15 scenarios total across 7 feature files in `features/`.

## Local Kubernetes Deployment

Deploy the full stack (products service + PostgreSQL) to a local K3D cluster.

### One-time setup

The cluster registry is plain HTTP. Two host-level tweaks are required before `make push` works. Run `make preflight` to check.

1. Add the registry hostname:
   ```bash
   echo "127.0.0.1 cluster-registry" | sudo tee -a /etc/hosts
   ```

2. Allow insecure registry access:
   ```bash
   sudo tee /etc/docker/daemon.json <<'EOF'
   {"insecure-registries": ["cluster-registry:5000"]}
   EOF
   sudo systemctl restart docker
   ```

### Deploy

```bash
make cluster          # create K3D cluster with registry
make build            # build the products image
make push             # push to cluster-registry
make deploy           # apply k8s manifests
```

Service is reachable at `http://localhost:8080`. Tear down with `make cluster-rm`.

## OpenShift CD Pipeline

The `.tekton/` folder contains Tekton manifests for a 6-task CI/CD pipeline triggered by GitHub webhooks on pushes to `master`:

```
clone → lint ──┐
               ├→ build → deploy → bdd
clone → tests ─┘
```

Lint and tests run in parallel after clone. The BDD task receives the deployed service URL via a `BASE_URL` parameter.

### Apply pipeline resources

```bash
oc apply -f .tekton/workspace.yaml
oc apply -f .tekton/tasks.yaml
oc apply -f .tekton/pipeline.yaml
oc apply -f .tekton/trigger-binding.yaml
oc apply -f .tekton/trigger-template.yaml
oc apply -f .tekton/event-listener.yaml
```

### Set up the webhook secret

```bash
oc create secret generic github-webhook-secret \
  --from-literal=secretToken='<shared-secret>'
```

### Get the webhook URL

```bash
oc get route cd-pipeline-listener -o jsonpath='https://{.spec.host}{"\n"}'
```

Configure the GitHub webhook with this URL, content type `application/json`, the shared secret, and "Just the push event." The EventListener's CEL filter restricts triggers to `refs/heads/master`.

### Verify

```bash
oc get pipelineruns --sort-by=.metadata.creationTimestamp
tkn pipelinerun logs -f <run-name>
```

## Project Structure

```
service/
├── __init__.py
├── config.py              # configuration
├── models.py              # Product model
├── routes.py              # REST API + admin UI routes
├── static/                # JS and CSS for admin pages
├── templates/             # HTML templates for admin pages
└── common/                # error handlers, logging, status codes

tests/
├── factories.py           # test data factory
├── test_models.py         # model unit tests
└── test_routes.py         # route unit tests

features/
├── environment.py         # Selenium setup / teardown
├── *.feature              # Gherkin scenarios
└── steps/                 # step implementations

k8s/
├── deployment.yaml        # products Deployment
├── service.yaml           # products Service
├── ingress.yaml           # Ingress (local K3D)
├── openshift/
│   ├── route.yaml         # OpenShift Route
│   └── postgres/          # PostgreSQL for OpenShift
└── postgres/              # PostgreSQL for local K3D

.tekton/
├── pipeline.yaml          # CD pipeline definition
├── tasks.yaml             # custom task definitions (lint, tests, deploy, bdd)
├── workspace.yaml         # PVC for pipeline workspace
├── event-listener.yaml    # EventListener + Route
├── trigger-binding.yaml   # TriggerBinding
└── trigger-template.yaml  # TriggerTemplate

.github/workflows/
└── ci.yml                 # GitHub Actions CI
```

## License

Copyright (c) 2016, 2025 [John Rofrano](https://www.linkedin.com/in/JohnRofrano/). All rights reserved.

Licensed under the Apache License. See [LICENSE](LICENSE)

This repository is part of the New York University (NYU) masters class: **CSCI-GA.2820-001 DevOps and Agile Methodologies** created and taught by [John Rofrano](https://cs.nyu.edu/~rofrano/), Adjunct Instructor, NYU Courant Institute, Graduate Division, Computer Science, and NYU Stern School of Business.
