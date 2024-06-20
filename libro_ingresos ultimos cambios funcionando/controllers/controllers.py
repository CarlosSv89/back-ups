# -*- coding: utf-8 -*-
# from odoo import http


# class LibroIngresos(http.Controller):
#     @http.route('/libro_ingresos/libro_ingresos/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/libro_ingresos/libro_ingresos/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('libro_ingresos.listing', {
#             'root': '/libro_ingresos/libro_ingresos',
#             'objects': http.request.env['libro_ingresos.libro_ingresos'].search([]),
#         })

#     @http.route('/libro_ingresos/libro_ingresos/objects/<model("libro_ingresos.libro_ingresos"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('libro_ingresos.object', {
#             'object': obj
#         })
