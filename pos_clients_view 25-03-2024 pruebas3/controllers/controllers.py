# -*- coding: utf-8 -*-
# from odoo import http


# class PosClientsView(http.Controller):
#     @http.route('/pos_clients_view/pos_clients_view/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/pos_clients_view/pos_clients_view/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('pos_clients_view.listing', {
#             'root': '/pos_clients_view/pos_clients_view',
#             'objects': http.request.env['pos_clients_view.pos_clients_view'].search([]),
#         })

#     @http.route('/pos_clients_view/pos_clients_view/objects/<model("pos_clients_view.pos_clients_view"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('pos_clients_view.object', {
#             'object': obj
#         })
