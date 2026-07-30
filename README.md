# Meter Invoice

## Overview

**Meter Invoice** is a custom Odoo module that extends the Accounting application by adding meter reading support to customer invoice lines. It enables utility-style billing by recording meter readings, automatically calculating consumption, and using the calculated consumption as the billed quantity.

This module was developed as part of an Odoo Developer take-home assignment.

## Features

* Adds **Previous**, **New**, and **Actual** meter reading columns to customer invoice lines.
* Automatically retrieves the **Previous** meter reading from the customer's most recent posted invoice containing the same product.
* Allows users to enter the current month's **New** meter reading.
* Validates that the **New** meter reading cannot be less than the **Previous** meter reading.
* Automatically computes **Actual = New − Previous**.
* Automatically synchronizes the invoice **Quantity** with the calculated consumption.
* Prevents manual editing of calculated fields to ensure data consistency.
* Includes automated unit tests for the core business logic.

## Module Structure

```text
meter_invoice/
├── models/
├── views/
├── tests/
├── security/
├── demo/
├── __manifest__.py
└── README.md
```

## Requirements

* Odoo 18
* Python 3.12 (or compatible with your Odoo installation)

## Installation

1. Clone the repository.

2. Copy the module into your Odoo custom addons directory.

3. Add the custom addons directory to the `addons_path` in `odoo.conf`.

4. Restart the Odoo server.

5. Update the Apps list.

6. Install the **Meter Invoice** module from the Apps menu.

Alternatively, install or upgrade the module from the command line:

```bash
python3 odoo-bin -c odoo.conf -d meter_invoice_dev -u meter_invoice
```

## Usage

1. Open the **Accounting** application.
2. Create or edit a Customer Invoice.
3. Add an invoice line and select a product.
4. The **Previous** reading is automatically populated from the latest posted invoice for the same customer and product.
5. Enter the **New** meter reading.
6. The **Actual** consumption is automatically calculated.
7. The invoice **Quantity** is automatically updated to match the calculated consumption.

## Running Tests

Run the automated tests with:

```bash
python3 odoo-bin \
    -c odoo.conf \
    -d meter_invoice_dev \
    -u meter_invoice \
    --test-enable \
    --stop-after-init
```

Example successful output:

```text
0 failed, 0 error(s)
```

## Dependencies

* `account`

## Design Decisions

* **Previous Reading** is read-only and automatically populated from invoice history.
* **New Reading** is entered by the user, stored with the invoice, and must be greater than or equal to the **Previous Reading**.
* **Actual Reading** is computed as:

```text
Actual = New Reading − Previous Reading
```

* **Quantity** is automatically synchronized with the calculated consumption to ensure billing accuracy.
* The previous reading lookup searches the latest posted invoice line for the same customer and product.

## Repository

GitHub Repository:

`https://github.com/trevor-gituru/odoo-meter-reading-module`

## Author

Trevor Gituru

