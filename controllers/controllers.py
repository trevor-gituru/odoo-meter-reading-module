# -*- coding: utf-8 -*-
# from odoo import http


# class MeterInvoice(http.Controller):
#     @http.route('/meter_invoice/meter_invoice', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/meter_invoice/meter_invoice/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('meter_invoice.listing', {
#             'root': '/meter_invoice/meter_invoice',
#             'objects': http.request.env['meter_invoice.meter_invoice'].search([]),
#         })

#     @http.route('/meter_invoice/meter_invoice/objects/<model("meter_invoice.meter_invoice"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('meter_invoice.object', {
#             'object': obj
#         })

