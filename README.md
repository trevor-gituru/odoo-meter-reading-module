# Meter Invoice

## Overview

**Meter Invoice** is a custom Odoo module that extends the Accounting application by adding meter reading support to customer invoice lines. It enables utility-style billing by recording meter readings, automatically calculating consumption, and using the calculated consumption as the billed quantity.

The module also extends the standard Odoo customer invoice PDF report by displaying meter readings for each invoice line.

This project was developed as part of an Odoo Developer take-home assignment.

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
- Includes GitHub Actions workflows for automated testing and linting.

---

## Module Structure

```text
meter_invoice/
├── .github/
│   └── workflows/
│       ├── lint.yml
│       └── odoo-tests.yml
├── controllers/
├── models/
├── tests/
├── views/
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

This repository includes automated CI workflows.

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
