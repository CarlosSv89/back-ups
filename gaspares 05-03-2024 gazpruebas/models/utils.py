from odoo import _
from odoo.exceptions import UserError
import json
import urllib.request

_GUID_REGEX = '^[{]?[0-9a-fA-F]{8}-([0-9a-fA-F]{4}-){3}[0-9a-fA-F]{12}[}]?$'

def make_gaspar_request(url, method, params=None):
    try:
        req = None
        if params:
            req = urllib.request.Request(url, data=json.dumps(params).encode('utf-8'), 
                                        headers={'Content-Type': 'application/json'}, method=method)
        else:
            req = urllib.request.Request(url, headers={'Content-Type': 'application/json'}, method=method)                                
        decResponse = urllib.request.urlopen(req).read().decode('utf-8')
        val = json.loads(decResponse)
        return val
    except urllib.error.HTTPError as e:
        raise UserError(e.read().decode('ISO-8859-1'))

def format_id_planta(id_planta):
    return id_planta.zfill(3)

def obtenerCentroDist(env):
    distCenters = env['gaspar.centro.distribucion'].search([])
    dc = None
    if not distCenters:
        raise UserError(_('There are not distribution centers, create one to continue.'))
    for distCenter in distCenters:
        dc = distCenter
        break
    return dc