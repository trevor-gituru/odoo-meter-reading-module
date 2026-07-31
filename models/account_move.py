# -*- coding: utf-8 -*-
from odoo import api, models


class AccountMove(models.Model):
    """
    Extend invoices to keep meter readings in sync with the selected
    customer.
    """

    _inherit = "account.move"

    @api.onchange("partner_id")
    def _onchange_partner_id_refresh_previous_reading(self):
        """
        Re-run the previous-reading lookup on every invoice line when the
        customer changes.

        account.move.line._onchange_previous_reading() only triggers off
        product_id (see that method's docstring for why move_id.partner_id
        can't be used as a trigger directly on the line). Without this,
        a line whose product was picked before the partner was set — or
        while switching from one customer to another — would keep a
        previous_reading looked up for the wrong customer (or none at
        all). Calling the line's onchange explicitly here keeps both
        paths (product changed, partner changed) in sync.
        """
        for line in self.invoice_line_ids:
            line._onchange_previous_reading()
