# -*- coding: utf-8 -*-
# from odoo import http


# class TemaGasRed(http.Controller):
#     @http.route('/tema_gas_red/tema_gas_red/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/tema_gas_red/tema_gas_red/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('tema_gas_red.listing', {
#             'root': '/tema_gas_red/tema_gas_red',
#             'objects': http.request.env['tema_gas_red.tema_gas_red'].search([]),
#         })

#     @http.route('/tema_gas_red/tema_gas_red/objects/<model("tema_gas_red.tema_gas_red"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('tema_gas_red.object', {
#             'object': obj
#         })
