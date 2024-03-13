# -*- coding: utf-8 -*-
# from odoo import http


# class Catalogo(http.Controller):
#     @http.route('/catalogo/catalogo/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/catalogo/catalogo/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('catalogo.listing', {
#             'root': '/catalogo/catalogo',
#             'objects': http.request.env['catalogo.catalogo'].search([]),
#         })

#     @http.route('/catalogo/catalogo/objects/<model("catalogo.catalogo"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('catalogo.object', {
#             'object': obj
#         })
