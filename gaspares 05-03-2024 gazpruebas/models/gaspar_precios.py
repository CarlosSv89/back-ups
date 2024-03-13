from . import utils
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class GasparPrecios(models.Model):
    _name = 'gaspar.precios'
    _description = 'Gaspar prices'
    _sql_constraints = [('gaspar_id_unique', 'UNIQUE(gaspar_id)', 'Gaspar ID field must be unique.')]

    name = fields.Char(string='Name')
    company_id = fields.Many2one(comodel_name='res.company', required=True, default=lambda self: self.env.company)
    precio = fields.Float(string='Price', required=True)
    tax_rate = fields.Float(string='Tax rate', required=True)
    region_zone = fields.Integer(string='Region zone')
    guid_gaspar = fields.Char(string='Gaspar ID')
    
    
    @api.model
    def create(self, vals):
        s = vals['name'].split('-')
        vals['region_zone'] = int(s[1])
        return super(GasparPrecios, self).create(vals)

    
    @api.constrains('guid_gaspar')
    def check_gaspar_id_validity(self):
        for price in self:
            if price.guid_gaspar and not price.guid_gaspar.match(utils._GUID_REGEX):
                raise UserError(_('Gaspar ID is invalid.'))


    def actualizar_precios_gaspar(self):
        for price in self:
            try:
                price = {
                    'priceValue': price.precio,
                    'reference': price.name,
                    'taxRate': price.tax_rate,
                    'regionZone': price.region_zone,
                    'productId': 1,
                }
                method = 'POST'
                #'http://<IP>:<PORT>/integrationAPI/'
                url = self.env['ir.config_parameter'].get_param('pos_route_config.gaspar_integracion_api') + '/prices'
                if price.guid_gaspar:
                    method = 'PUT'
                    url = url + '/' + price.guid_gaspar
                response = utils.make_gaspar_request(url=url , params=price, method=method)
                # TODO verificar el resultado de la respuesta
                #if method == 'POST':
                #    price.guid_gaspar = response['guid']
            except Exception as e:
                raise UserError(_('No es posible guardar precio en gaspar. <br/>Error: %s' % e))


class GasparCondicionesPago(models.Model):
    _name = 'gaspar.condiciones.pago'
    _description = "Gaspar payment conditions"

    name = fields.Char(string='Name')
    company_id = fields.Many2one(comodel_name='res.company', required=True, default=lambda self: self.env.company)
    gaspar_id = fields.Char(string='Code', required=True)


    # @api.constrains('gaspar_id')
    # def check_gaspar_id_validity(self):
    #     if not re.match(_GUID_REGEX, self.gaspar_id):
    #         raise UserError(_('Gaspar ID does not match the expected format'))



class GasparDistributionCenter(models.Model):
    _name = 'gaspar.centro.distribucion'
    _description = 'Distribution center'

    name = fields.Char(string='Name', required=True)
    company_id = fields.Many2one(comodel_name='res.company', required=True, default=lambda self: self.env.company)
    guid_gaspar = fields.Char(string='Gaspar ID', required=True)
    code = fields.Char(string='Code', required=True)
    center_key = fields.Char(string='Center key', required=True)

    @api.constrains('guid_gaspar')
    def check_gaspar_id_validity(self):
        for dc in self:
            if dc.guid_gaspar and not dc.guid_gaspar.match(utils._GUID_REGEX):
                raise UserError(_('Gaspar ID is invalid.'))

