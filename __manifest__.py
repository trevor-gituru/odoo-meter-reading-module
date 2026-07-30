# -*- coding: utf-8 -*-
{
    "name": "Meter Invoice",
    "summary": "Adds meter reading support to customer invoices",
    "description": """
Extends the Odoo Accounting module by adding Previous, New,
and Actual meter reading fields to invoice lines. The module
automatically calculates consumption, updates the invoice
quantity, and displays the readings on invoice views and reports.
    """,
    "author": "Trevor Gituru",
    "website": "https://github.com/trevor-gituru/odoo-meter-reading-module",
    "category": "Accounting",
    "version": "18.0.1.0.0",
    # Required module
    "depends": ["account"],
    # Data files loaded during installation
    "data": [
        "views/views.xml",
        "views/templates.xml",
    ],
    # Demo data
    "demo": [],
    "installable": True,
    "application": False,
    "license": "LGPL-3",
}
