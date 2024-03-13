# -*- coding: utf-8 -*-
# from odoo import http


# class FacturaContado(http.Controller):
#     @http.route('/factura_contado/factura_contado/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/factura_contado/factura_contado/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('factura_contado.listing', {
#             'root': '/factura_contado/factura_contado',
#             'objects': http.request.env['factura_contado.factura_contado'].search([]),
#         })

#     @http.route('/factura_contado/factura_contado/objects/<model("factura_contado.factura_contado"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('factura_contado.object', {
#             'object': obj
#         })
