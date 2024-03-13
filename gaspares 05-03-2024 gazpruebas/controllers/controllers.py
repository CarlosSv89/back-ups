# -*- coding: utf-8 -*-
# from odoo import http


# class Gtmz/gaspares(http.Controller):
#     @http.route('/gtmz/gaspares/gtmz/gaspares/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/gtmz/gaspares/gtmz/gaspares/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('gtmz/gaspares.listing', {
#             'root': '/gtmz/gaspares/gtmz/gaspares',
#             'objects': http.request.env['gtmz/gaspares.gtmz/gaspares'].search([]),
#         })

#     @http.route('/gtmz/gaspares/gtmz/gaspares/objects/<model("gtmz/gaspares.gtmz/gaspares"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('gtmz/gaspares.object', {
#             'object': obj
#         })
