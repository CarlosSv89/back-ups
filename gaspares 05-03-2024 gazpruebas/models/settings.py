from odoo import api, fields, models


class Company(models.Model):
    _inherit = 'res.company'

    gaspar_integracion_api = fields.Char(string='Gaspar Integration API', readonly=False)
    

class RouteConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    gaspar_integracion_api = fields.Char(string='Gaspar Integration API', 
        related="company_id.gaspar_integracion_api", readonly=False)
