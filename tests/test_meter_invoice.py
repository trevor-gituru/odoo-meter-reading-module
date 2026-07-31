# -*- coding: utf-8 -*-
"""
Unit tests for the Meter Invoice module.

These tests verify the custom business logic added to invoice lines,
including meter consumption calculation, quantity synchronization,
and retrieval of previous meter readings.
"""
from odoo.exceptions import ValidationError
from odoo.tests import Form
from odoo.tests.common import TransactionCase


class TestMeterInvoice(TransactionCase):
    """
    Test suite for the Meter Invoice module.

    The tests validate:
    * Actual meter consumption calculation.
    * Synchronization of invoice quantity with consumption.
    * Retrieval of the previous meter reading from invoice history.
    """

    @classmethod
    def setUpClass(cls):
        """
        Create common test data used by all test cases.

        Test data includes:
        * Two customers (one with invoice history, one without)
        * Two products (one with invoice history, one without)
        * A posted customer invoice containing an initial meter reading,
          which acts as invoice history for later tests.
        """
        super().setUpClass()

        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test Water Customer",
            }
        )
        cls.other_partner = cls.env["res.partner"].create(
            {
                "name": "Customer Without History",
            }
        )

        cls.product = cls.env["product.product"].create(
            {
                "name": "Water Consumption",
                "type": "service",
            }
        )
        cls.other_product = cls.env["product.product"].create(
            {
                "name": "Product Without History",
                "type": "service",
            }
        )

        # Create and post an initial invoice using the Form helper so that
        # onchanges (including our own _onchange_previous_reading) fire the
        # same way they would from the UI. This invoice's new_reading
        # (100.0) becomes the "previous_reading" for the customer's next
        # invoice on the same product.
        move_form = Form(
            cls.env["account.move"].with_context(default_move_type="out_invoice")
        )
        move_form.partner_id = cls.partner
        with move_form.invoice_line_ids.new() as line_form:
            line_form.product_id = cls.product
            line_form.new_reading = 100.0
        cls.initial_move = move_form.save()
        cls.initial_move.action_post()

        cls.initial_line = cls.initial_move.invoice_line_ids.filtered(
            lambda line: line.product_id == cls.product
        )

    def _create_draft_line(self, partner, product, new_reading):
        """
        Helper: create a draft (unposted) invoice with a single line for
        the given partner/product, returning that line.

        Compute-only tests deliberately use a draft invoice rather than
        self.initial_line: quantity is a plain (non-computed) field that
        _compute_actual_reading also assigns to, and assigning a field on
        an already-saved record routes through the normal write() path.
        Odoo's accounting module can restrict/ignore writes to certain
        fields (like quantity) on posted journal items, which would make
        these tests fail for reasons unrelated to the compute logic itself.
        """
        move_form = Form(
            self.env["account.move"].with_context(default_move_type="out_invoice")
        )
        move_form.partner_id = partner
        with move_form.invoice_line_ids.new() as line_form:
            line_form.product_id = product
            line_form.new_reading = new_reading
        move = move_form.save()
        return move.invoice_line_ids.filtered(lambda line: line.product_id == product)

    def test_actual_reading_is_computed(self):
        """
        Verify that actual consumption is computed correctly.

        Expected:
            Actual = New - Previous
        """
        line = self._create_draft_line(self.other_partner, self.other_product, 75.0)
        line.write({"previous_reading": 20.0, "new_reading": 75.0})

        self.assertEqual(
            line.actual_reading,
            55.0,
            "Actual reading should equal New Reading minus Previous Reading.",
        )

    def test_quantity_matches_actual(self):
        """
        Verify that invoice quantity matches the calculated
        meter consumption.
        """
        line = self._create_draft_line(self.other_partner, self.other_product, 90.0)
        line.write({"previous_reading": 30.0, "new_reading": 90.0})

        self.assertEqual(
            line.quantity,
            line.actual_reading,
            "Quantity should be synchronized with the actual reading.",
        )
        self.assertEqual(line.quantity, 60.0)

    def test_previous_reading_is_loaded(self):
        """
        Verify that the previous meter reading is obtained from
        the customer's latest posted invoice containing the
        same product.
        """
        move_form = Form(
            self.env["account.move"].with_context(default_move_type="out_invoice")
        )
        move_form.partner_id = self.partner
        with move_form.invoice_line_ids.new() as line_form:
            # Setting product_id (together with the partner already set on
            # the move) triggers _onchange_previous_reading.
            line_form.product_id = self.product
            line_form.new_reading = 150.0
        new_move = move_form.save()

        new_line = new_move.invoice_line_ids.filtered(
            lambda line: line.product_id == self.product
        )

        self.assertEqual(
            new_line.previous_reading,
            100.0,
            "Previous reading should be loaded from the customer's most "
            "recent posted invoice for the same product.",
        )
        self.assertEqual(new_line.actual_reading, 50.0)

    def test_previous_reading_defaults_to_zero(self):
        """
        Verify that the previous reading defaults to zero when
        no matching invoice history exists.
        """
        move_form = Form(
            self.env["account.move"].with_context(default_move_type="out_invoice")
        )
        move_form.partner_id = self.other_partner
        with move_form.invoice_line_ids.new() as line_form:
            line_form.product_id = self.other_product
            line_form.new_reading = 40.0
        new_move = move_form.save()

        new_line = new_move.invoice_line_ids.filtered(
            lambda line: line.product_id == self.other_product
        )

        self.assertEqual(
            new_line.previous_reading,
            0.0,
            "Previous reading should default to 0.0 when no invoice "
            "history exists for the customer/product combination.",
        )
        self.assertEqual(new_line.actual_reading, 40.0)

    def test_new_reading_below_previous_raises_validation_error(self):
        """
        Verify that saving a new reading lower than the previous reading
        is rejected by the model constraint (meters only count up).
        """
        line = self._create_draft_line(self.other_partner, self.other_product, 50.0)
        with self.assertRaises(ValidationError):
            line.write({"previous_reading": 80.0, "new_reading": 50.0})
