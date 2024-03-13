# -*- coding: utf-8 -*-
# from odoo import http


# class ClaseCliente(http.Controller):
#     @http.route('/clase_cliente/clase_cliente/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/clase_cliente/clase_cliente/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('clase_cliente.listing', {
#             'root': '/clase_cliente/clase_cliente',
#             'objects': http.request.env['clase_cliente.clase_cliente'].search([]),
#         })

#     @http.route('/clase_cliente/clase_cliente/objects/<model("clase_cliente.clase_cliente"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('clase_cliente.object', {
#             'object': obj
#         })
