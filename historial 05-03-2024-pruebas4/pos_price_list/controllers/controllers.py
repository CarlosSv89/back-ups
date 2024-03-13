# -*- coding: utf-8 -*-
# from odoo import http


# class PosPriceList(http.Controller):
#     @http.route('/pos_price_list/pos_price_list/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/pos_price_list/pos_price_list/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('pos_price_list.listing', {
#             'root': '/pos_price_list/pos_price_list',
#             'objects': http.request.env['pos_price_list.pos_price_list'].search([]),
#         })

#     @http.route('/pos_price_list/pos_price_list/objects/<model("pos_price_list.pos_price_list"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('pos_price_list.object', {
#             'object': obj
#         })
