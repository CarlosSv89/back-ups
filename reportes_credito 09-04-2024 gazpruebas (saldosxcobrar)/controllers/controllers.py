# -*- coding: utf-8 -*-
# from odoo import http


# class Gtmz/reportesCredito(http.Controller):
#     @http.route('/gtmz/reportes_credito/gtmz/reportes_credito/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/gtmz/reportes_credito/gtmz/reportes_credito/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('gtmz/reportes_credito.listing', {
#             'root': '/gtmz/reportes_credito/gtmz/reportes_credito',
#             'objects': http.request.env['gtmz/reportes_credito.gtmz/reportes_credito'].search([]),
#         })

#     @http.route('/gtmz/reportes_credito/gtmz/reportes_credito/objects/<model("gtmz/reportes_credito.gtmz/reportes_credito"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('gtmz/reportes_credito.object', {
#             'object': obj
#         })
