# -*- coding: utf-8 -*-

from odoo import fields, models


class AccountMoveLine(models.Model):
    """
    Extend invoice lines to support meter readings.

    This model adds the previous, new, and actual meter reading
    fields required for calculating customer consumption on
    invoice lines.
    """

    _inherit = "account.move.line"

    previous_reading = fields.Float(
        string="Previous",
        help="Previous meter reading from the customer's last posted invoice.",
    )

    new_reading = fields.Float(
        string="New", help="Current meter reading captured for this invoice."
    )

    actual_reading = fields.Float(
        string="Actual",
        help="Difference between the current and previous meter readings.",
    )
