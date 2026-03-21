# NYU DevOps Project Template

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Language-Python-blue.svg)](https://python.org/)

#This service provides a REST API for managing a catalog of products. It allows users to create, retrieve, update, delete, and list products stored in a PostgreSQL database.

## Overview

The Product Catalog Service is a backend application built with Flask that exposes RESTful endpoints to manage product data.

It supports the following operations:
- Create a product
- Retrieve a product by ID
- Update a product
- Delete a product
- List all products

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

## API Endpoints

### Root Endpoint
GET /

Returns basic service information and available paths.

### Create a Product
POST /products

Creates a new product.

### Retrieve a Product
GET /products/{id}

Returns a product by its ID.

### Update a Product
PUT /products/{id}

Updates an existing product.

### Delete a Product
DELETE /products/{id}

Deletes a product by its ID.

### List Products
GET /products

Returns a list of all products.


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
