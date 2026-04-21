# NYU DevOps Project Template

<!-- CI and Codecov badges added for visibility -->

[![CI](https://github.com/CSCI-GA-2820-SP26-001/products/actions/workflows/ci.yml/badge.svg)](https://github.com/CSCI-GA-2820-SP26-001/products/actions)

[![codecov](https://codecov.io/gh/CSCI-GA-2820-SP26-001/products/branch/master/graph/badge.svg)](https://codecov.io/gh/CSCI-GA-2820-SP26-001/products)

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Language-Python-blue.svg)](https://python.org/)

This service provides a REST API for managing a catalog of products. It allows users to create, retrieve, update, delete, and list products stored in a PostgreSQL database.

## Overview

The Product Catalog Service is a backend application built with Flask that exposes RESTful endpoints to manage product data.

It supports the following operations:
- Create a product
- Retrieve a product by ID
- Update a product
- Delete a product
- List all products
- Use a simple admin UI page for product update workflows

## Product Data Model

A Product has the following attributes:

| Field        | Type     | Description                         |
|-------------|---------|-------------------------------------|
| id          | Integer | Unique identifier (auto-generated) |
| name        | String  | Name of the product                |
| description | String  | Description of the product         |
| price       | Decimal | Price of the product               |
| category    | String  | Product category                   |
| available   | Boolean | Availability (default: True)       |

## Running the Service

Start the service locally using honcho:

```bash
make run
```

The service will be available at `http://localhost:8080`.

Admin UI pages:

- `http://localhost:8080/admin/products/create` — Add a new product to the catalog.
- `http://localhost:8080/admin/products/update` — Retrieve a product by id, edit fields, and submit updates.
- `http://localhost:8080/admin/products/delete` — Delete a product by id.
- `http://localhost:8080/admin/products/list` — View all products in the catalog.

## Running Tests

Run the full test suite with coverage:

```bash
make test
```

This runs pytest with a minimum coverage threshold of 95%.

## Linting

Check code style against PEP8:

```bash
make lint
```

## Local Kubernetes Deployment

Deploy the full stack (products service + PostgreSQL) to a local K3D cluster.
Both images — the products container and `postgres:15` — are served from the
in-cluster `cluster-registry:5000` so that `kubectl apply` always pulls via a
registry (this avoids a known containerd/k3d issue with `k3d image import`
and multi-manifest attestation digests).

### One-time local setup

The cluster registry is plain HTTP, which the local Docker daemon refuses by
default. Two one-time machine-level tweaks are required before `make push` /
`make seed-postgres` work. `make preflight` validates both and prints the
exact fix command if something is missing.

1. Let the local docker CLI resolve `cluster-registry` to the loopback address:

   ```bash
   echo "127.0.0.1 cluster-registry" | sudo tee -a /etc/hosts
   ```

2. Tell the docker daemon that `cluster-registry:5000` is an insecure
   (plain-HTTP) registry, then restart docker:

   ```bash
   sudo tee /etc/docker/daemon.json <<'EOF'
   {"insecure-registries": ["cluster-registry:5000"]}
   EOF
   sudo systemctl restart docker    # or restart Docker Desktop
   ```

### Deploy sequence

```bash
make preflight        # sanity-check the two host-level tweaks above
make cluster          # create K3D cluster with load balancer + registry
make seed-postgres    # pull postgres:15 and push it to cluster-registry
make build            # build the products image
make push             # push the products image to cluster-registry
make deploy           # kubectl apply -R -f k8s/
```

Once the pods are ready, the service is reachable through the ingress at
`http://localhost:8080/` (e.g. `curl http://localhost:8080/health`).

Tear down with `make cluster-rm`.

## API Endpoints

### Root Endpoint

`GET /`

Returns basic service information and available paths.

**Response:**

```json
{
  "name": "Product Catalog Service",
  "version": "1.0",
  "paths": ["/products", "/products/{id}", "/products/{id}/purchase"]
}
```

### Create a Product

`POST /products`

Creates a new product. Requires `Content-Type: application/json`.

**Request Body (required fields marked with *):**

| Field       | Type    | Required | Description                    |
|-------------|---------|----------|--------------------------------|
| name        | String  | *        | Name of the product            |
| price       | Decimal | *        | Price of the product           |
| category    | String  | *        | Product category               |
| description | String  |          | Description (default: "")      |
| available   | Boolean |          | Availability (default: true)   |
| stock       | Integer |          | Units in stock (default: 0). If omitted, stock is 0 and `available` is unchanged. If `stock` is sent and is `<= 0`, `available` is set to false. |

**Example:**

```json
{
  "name": "Widget",
  "description": "A useful widget",
  "price": 19.99,
  "category": "gadgets",
  "available": true
}
```

**Response:** `201 Created` with the created product and a `Location` header.

### Retrieve a Product

`GET /products/{id}`

Returns a product by its ID.

**Response:** `200 OK` with the product, or `404 Not Found` if it does not exist.

### Update a Product

`PUT /products/{id}`

Updates an existing product. Requires `Content-Type: application/json`. The request body uses the same fields as Create.

**Response:** `200 OK` with the updated product, or `404 Not Found` if it does not exist.

### Admin Product Create UI

`GET /admin/products/create`

Renders a lightweight admin page that supports:
- filling in `name`, `description`, `price`, `category`, `stock`, and `available`
- submitting the form to create a new product
- viewing success/error messages with the created product details

### Admin Product Delete UI

`GET /admin/products/delete`

Renders a lightweight admin page that supports:
- entering a product id
- deleting the product and viewing a success message
- displaying an error if the product does not exist

### Admin Product List UI

`GET /admin/products/list`

Renders a lightweight admin page that supports:
- pressing a "List All" button to retrieve every product
- displaying results in a table with id, name, category, price, stock, and availability
- showing a message when no products exist

### Admin Product Update UI

`GET /admin/products/update`

Renders a lightweight admin page that supports:
- retrieving an existing product by id
- editing `name`, `description`, `price`, `category`, `stock`, and `available`
- submitting updates and viewing success/error messages with updated details

### Purchase a Product

`PUT /products/{id}/purchase`

Purchases one unit (decrements stock by 1). No request body is required.

**Response:** `200 OK` with the updated product. Returns `409 Conflict` if the product is unavailable or has no stock remaining. Returns `404 Not Found` if the id does not exist. When stock reaches zero after purchase, `available` is set to `false`.

### Delete a Product

`DELETE /products/{id}`

Deletes a product by its ID. **Idempotent:** returns `204 No Content` even if the product does not exist (the resource is already absent).

**Response:** `204 No Content` with an empty body.

### List Products

`GET /products`

Returns a JSON array of products. With no query parameters, all products are returned.

**Query parameters (optional):**

| Parameter | Description |
|-----------|-------------|
| `category` | When present and non-empty after trimming whitespace, only products whose `category` matches this value **case-insensitively** are returned. If the parameter is omitted, empty, or only whitespace, all products are returned. If no products match, the response is an empty array. When `category` appears more than once in the query string, the first value is used. |

**Examples:** `GET /products`, `GET /products?category=Electronics`, `GET /products?category=electronics`

**Response:** `200 OK` with a JSON array of products.

## Contents

The project contains the following:

```text
.gitignore          - this will ignore vagrant and other metadata files
.flaskenv           - Environment variables to configure Flask
.gitattributes      - File to gix Windows CRLF issues
.devcontainers/     - Folder with support for VSCode Remote Containers
dot-env-example     - copy to .env to use environment variables
pyproject.toml      - Poetry list of Python libraries required by your code

service/                   - service python package
├── __init__.py            - package initializer
├── config.py              - configuration parameters
├── models.py              - module with business models
├── routes.py              - module with service routes
└── common                 - common code package
    ├── cli_commands.py    - Flask command to recreate all tables
    ├── error_handlers.py  - HTTP error handling code
    ├── log_handlers.py    - logging setup code
    └── status.py          - HTTP status constants

tests/                     - test cases package
├── __init__.py            - package initializer
├── factories.py           - Factory for testing with fake objects
├── test_cli_commands.py   - test suite for the CLI
├── test_models.py         - test suite for business models
└── test_routes.py         - test suite for service routes
```

## License

Copyright (c) 2016, 2025 [John Rofrano](https://www.linkedin.com/in/JohnRofrano/). All rights reserved.

Licensed under the Apache License. See [LICENSE](LICENSE)

This repository is part of the New York University (NYU) masters class: **CSCI-GA.2820-001 DevOps and Agile Methodologies** created and taught by [John Rofrano](https://cs.nyu.edu/~rofrano/), Adjunct Instructor, NYU Courant Institute, Graduate Division, Computer Science, and NYU Stern School of Business.

## Running BDD Tests

This project uses **Behave** and **Selenium** for browser-based BDD testing.

### Install BDD dependencies

```bash
pipenv install --dev behave selenium
