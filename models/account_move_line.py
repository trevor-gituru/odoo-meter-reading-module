# -*- coding: utf-8 -*-

from odoo import api, fields, models


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
        compute="_compute_actual_reading",
        store=True,
        readonly=True,
        help="Difference between the current and previous meter readings.",
    )

    @api.depends("previous_reading", "new_reading")
    def _compute_actual_reading(self):
        """
        Compute the actual meter consumption and synchronize the invoice quantity.

        Actual consumption is calculated as:

            Actual = New Reading - Previous Reading

        The computed consumption is also assigned to the invoice quantity
        to ensure the billed quantity matches the customer's meter usage.
        """
        for line in self:
            actual = line.new_reading - line.previous_reading

            line.actual_reading = actual
            line.quantity = actual
