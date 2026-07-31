# Meter Invoice

## Overview

**Meter Invoice** is a custom Odoo module that extends the Accounting application by adding meter reading support to customer invoice lines. It enables utility-style billing by recording meter readings, automatically calculating consumption, and using the calculated consumption as the billed quantity.

The module also extends the standard Odoo customer invoice PDF report by displaying meter readings for each invoice line.

This project was developed as part of an Odoo Developer take-home assignment.

**Live demo:** [https://odoo-meter-reading-module-latest-test.onrender.com/](https://odoo-meter-reading-module-latest-test.onrender.com/)
Deployed on Render as a Web Service running the `latest-test` image (see [Docker Image & Deployment](#docker-image--deployment) below). Running on Render's free tier — the instance may take up to a minute to wake up if it's been idle.

---

## Features

- Adds **Previous**, **New**, and **Actual** meter reading fields to customer invoice lines.
- Automatically retrieves the **Previous** meter reading from the customer's most recent posted invoice containing the same product.
- Allows users to enter the current month's **New** meter reading.
- Validates that the **New** meter reading cannot be less than the **Previous** meter reading.
- Automatically computes:

  ```
  Actual = New − Previous
  ```

- Automatically synchronizes the invoice **Quantity** with the calculated consumption.
- Prevents manual editing of calculated fields to ensure data consistency.
- Extends the customer invoice PDF report to include meter readings.
- Includes automated unit tests for the core business logic.
- Includes GitHub Actions workflows for automated testing, linting, and Docker image builds.
- Packaged as a Docker image with a configurable entrypoint, deployable to any host that accepts environment variables.

---

## Module Structure

```text
meter_invoice/
├── .github/
│   └── workflows/
│       ├── lint.yml
│       ├── odoo-tests.yml
│       └── docker-build-push.yml
├── controllers/
├── models/
├── tests/
├── views/
├── docker/
│   └── entrypoint.sh
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── __init__.py
├── __manifest__.py
├── README.md
└── requirements.txt (optional)
```

---

## Requirements

- Odoo 18
- Python 3.12 (or compatible with your Odoo installation)
- PostgreSQL
- Docker & Docker Compose (only required for running the containerized image — see [Docker Image & Deployment](#docker-image--deployment))

---

## Installation

1. Clone the repository.

2. Copy the module into your custom addons directory.

3. Add the directory to your `addons_path`.

4. Restart Odoo.

5. Update the Apps list.

6. Install **Meter Invoice**.

Or update from the command line:

```bash
python3 odoo-bin \
    -c odoo.conf \
    -d meter_invoice_dev \
    -u meter_invoice
```

---

## Usage

1. Open **Accounting**.
2. Create or edit a Customer Invoice.
3. Add an invoice line.
4. Select a product.
5. The **Previous Reading** is automatically populated.
6. Enter the **New Reading**.
7. The module calculates the **Actual Reading**.
8. The invoice **Quantity** is automatically updated.
9. Print the invoice to display meter readings in the PDF report.

---

## Running Tests

Run the module tests with:

```bash
python3 odoo-bin \
    -c odoo.conf \
    -d meter_invoice_test \
    -i meter_invoice \
    --without-demo=all \
    --test-enable \
    --stop-after-init
```

Expected output:

```text
0 failed, 0 error(s)
```

---

## Code Quality

Python linting:

```bash
ruff check .
```

XML validation:

```bash
xmllint --noout views/*.xml
```

---

## GitHub Actions

This repository includes automated CI/CD workflows for testing, linting, and Docker image builds.

### Odoo Tests

The **odoo-tests.yml** workflow automatically:

- Creates a PostgreSQL database
- Creates an Odoo database user
- Checks out Odoo 18
- Installs Python dependencies
- Copies the custom module
- Creates a test database
- Installs the module
- Runs automated unit tests
- Uploads test logs as workflow artifacts

The workflow runs on:

- Pushes to:
  - `main`
  - `develop`
- Pull requests targeting:
  - `main`
  - `develop`
- Manual workflow dispatch

---

### Lint Workflow

The **lint.yml** workflow automatically:

- Runs Ruff for Python linting
- Validates XML files using `xmllint`

This helps ensure code quality before merging changes.

---

## Docker Image & Deployment

The module and a full Odoo 18 environment are packaged into a single Docker image, built and pushed automatically by the **Build and Push Docker Image** workflow (`.github/workflows/docker-build-push.yml`).

### What the workflow does

- Checks out the repository and builds the image from the root `Dockerfile`.
- Logs in to and pushes to **GitHub Container Registry (GHCR)**.
- Tags every build with:
  - An immutable short commit SHA (e.g. `ghcr.io/trevor-gituru/odoo-meter-reading-module:1a2b3c4d5e6f`)
  - A floating environment tag: `latest-prod` when built from `main`, `latest-test` for any other branch (e.g. `develop`)
- Passes the branch being built as the `MODULE_BRANCH` build argument, so the image's Dockerfile clones the matching branch of this module into the image.

Runs on:

- Pushes to:
  - `main`
  - `develop`
- Manual workflow dispatch

### Live deployment

The [live demo](https://odoo-meter-reading-module-latest-test.onrender.com/) runs on **Render** as a Web Service, pulling the `ghcr.io/trevor-gituru/odoo-meter-reading-module:latest-test` image directly — no build step happens on Render itself, it just runs the image the workflow already built and pushed.

All runtime configuration is supplied via environment variables set in Render's dashboard, matching `.env.example` in this repo:

| Variable | Description |
|---|---|
| `DB_HOST` / `DB_PORT` / `DB_USER` / `DB_PASSWORD` | PostgreSQL connection details |
| `DB_NAME` | Name of an existing database Odoo should use |
| `ADMIN_PASSWORD` | Odoo master password (database management, not user login) |
| `AUTO_INIT` / `INIT_MODULES` | Used only for the initial module installation, then left unset |

### Running the image locally

```bash
cp .env.example .env
# edit .env with real values
docker compose pull
docker compose up
```

`docker-compose.yml` pulls the tagged image (`IMAGE_TAG` in `.env`, e.g. `latest-test`) rather than building locally, so it runs the exact same image as the live deployment.

---

## Dependencies

- `account`

---

## Design Decisions

- Previous Reading is automatically populated from the customer's latest posted invoice.
- Previous Reading is read-only.
- New Reading is entered manually.
- Actual Reading is computed automatically.

```
Actual = New Reading − Previous Reading
```

- Quantity always matches the calculated consumption.
- Previous readings are retrieved using the latest posted invoice for the same customer and product.
- Invoice reports are extended using QWeb template inheritance.
- Runtime configuration (database connection, admin password, module init) is entirely environment-variable-driven, so the same Docker image runs unmodified across local, CI, and hosted environments.

---

## Contributing

Development follows a simple Git workflow.

### Branch Strategy

```
main
│
└── develop
    │
    ├── feature/<feature-name>
    ├── fix/<bug-name>
    └── chore/<task>
```

### Development Process

1. Create a branch from `develop`.

```bash
git checkout develop
git pull
git checkout -b feature/add-meter-report
```

2. Make changes.

3. Run checks locally.

```bash
ruff check .
xmllint --noout views/*.xml
```

4. Commit using Conventional Commits.

Examples:

```text
feat: add invoice report meter readings
fix: validate new meter reading
test: add meter reading unit tests
ci: add Odoo test workflow
docs: update README
```

5. Push your branch.

6. Open a Pull Request into **develop**.

7. After review and passing GitHub Actions, merge into **develop**.

8. Release stable changes by merging **develop** into **main**.

---

## Repository

https://github.com/trevor-gituru/odoo-meter-reading-module

---

## Author

**Trevor Gituru**
