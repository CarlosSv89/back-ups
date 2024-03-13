# -*- coding: utf-8 -*-
# from odoo import http


# class PosOrderValidation(http.Controller):
#     @http.route('/pos_order_validation/pos_order_validation/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/pos_order_validation/pos_order_validation/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('pos_order_validation.listing', {
#             'root': '/pos_order_validation/pos_order_validation',
#             'objects': http.request.env['pos_order_validation.pos_order_validation'].search([]),
#         })

#     @http.route('/pos_order_validation/pos_order_validation/objects/<model("pos_order_validation.pos_order_validation"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('pos_order_validation.object', {
#             'object': obj
#         })
