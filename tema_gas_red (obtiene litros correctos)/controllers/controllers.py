# -*- coding: utf-8 -*-
# from odoo import http
# from odoo.http import request, Response
# import json


# class TemaGasRed(http.Controller):
#     @http.route('/tema_gas_red/get_litros/',type='json', methods=['POST'], auth='public', csrf=False)
#     def get_litros(self, **kw):
#       sessionId = int(kw.get('sessionId'))
#       session = http.request.env['pos.session'].browse(sessionId)
#       total_lt = session.get_total_lt()
#       res = {
#         'total_lt': total_lt
#       }
#       return Response(json.dumps(res), content_type='application/json;charset=utf-8', status=200)
      