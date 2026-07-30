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
        help="Previous meter reading retrieved from the customer's most recent posted invoice for the same product.",
    )

    new_reading = fields.Float(
        string="New", help="Current meter reading captured for this invoice."
    )

    actual_reading = fields.Float(
        string="Actual",
        compute="_compute_actual_reading",
        store=True,
        readonly=True,
        precompute=True,
        help="Difference between the current and previous meter readings.",
    )
    quantity = fields.Float(
        compute="_compute_actual_reading",
        store=True,
        readonly=True,
        precompute=True,
        help="Automatically set to match the actual meter consumption "
        "(New Reading minus Previous Reading). Not editable directly; "
        "correct the readings instead.",
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

    @api.onchange("product_id")
    def _onchange_previous_reading(self):
        """
        Populate the previous meter reading from the customer's most
        recent posted invoice line for the selected product.
        If no previous reading exists, the value defaults to 0.0.
        """
        for line in self:
            line.previous_reading = 0.0
            if not line.product_id or not line.partner_id:
                continue
            domain = [
                ("partner_id", "=", line.partner_id.id),
                ("move_id.move_type", "=", "out_invoice"),
                ("move_id.state", "=", "posted"),
                ("product_id", "=", line.product_id.id),
            ]
            if not isinstance(line.id, models.NewId):
                domain.append(("id", "!=", line.id))
            if not isinstance(line.move_id.id, models.NewId):
                domain.append(("move_id", "!=", line.move_id.id))
            previous_line = self.env["account.move.line"].search(
                domain, order="id desc", limit=1
            )
            if previous_line:
                line.previous_reading = previous_line.new_reading
