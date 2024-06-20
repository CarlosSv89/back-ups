# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request, Response
import requests
import logging
import json

_logger = logging.getLogger(__name__)

class EndpointsZae(http.Controller):
  @http.route('/api/evaluacion', csrf=False, auth='public', methods=['GET'], type='http', cors='*')
  def getEvaluacionRecords(self, **kw):
    # get headers
    headersReq = request.httprequest.headers
    # Credenciales de acceso
    login = headersReq.get('login', False)
    password = headersReq.get('password', False)
    db = 'jpedroza-p-gtmz-gazpruebas-12788612'
    # Chek if login or password are correct
    if not login or not password:
      return Response(json.dumps({"res": "missing login or password"}), content_type='application/json', status=400)
    else:
      try:
        # Realizar la solicitud POST para iniciar sesión y obtener el token de sesión
        login_url = 'https://jpedroza-p-gtmz-gazpruebas-12788612.dev.odoo.com/web/session/authenticate'
        login_data = {'jsonrpc': '2.0', 'params': {'login': login, 'password': password, "db": db}}
        login_response = requests.post(login_url, json=login_data)
        login_result = login_response.json()

        
        uid = login_result['result']['uid']
        _logger.warning(f' user id: {uid}')
        
        if "evaluacion_mensual.evaluacion_mensual" not in request.env:
          return Response(json.dumps({"res": "model evaluacion_mensual not found"}), content_type='application/json', status=404)
        
        # jsonrpc POST request to read data
        data_url = "https://jpedroza-p-gtmz-gazpruebas-12788612.dev.odoo.com/jsonrpc"
        
        data_read = {
          'jsonrpc': '2.0',
          'method': 'call',
          'params': {
            'service': 'object',
            'method': 'execute_kw',
            'args': [
                db,  # nombre de la base de datos
                uid,  # ID del usuario
                password,  # contraseña
                'evaluacion_mensual.evaluacion_mensual',  # modelo
                'search_read',  # método
                [[]],  # IDs de los registros
                {'fields': ['id', 'name']} # can limit with 'limit': <n>
            ],
          },
        }
        response_read = requests.post(data_url, data=json.dumps(data_read), headers={'content-type': 'application/json'})
        
        _logger.warning("respuesta: %s", response_read.json())
        
        headers = {
          "content-type": "application/json",
        }
        
        return Response(json.dumps(response_read.json()['result']), headers=headers, status=200)
      except Exception as e:
        return Response(json.dumps({"message": str(e), "status": 500}), content_type='application/json', status=500)