from email.mime import base
from . import utils
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import re


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
    
    
    # @api.model
    # def create(self, vals):
    #     s = vals['name'].split('-')
    #     vals['region_zone'] = int(s[1])
    #     return super(GasparPrecios, self).create(vals)

    @api.onchange('name')
    def name_on_change(self):
        try:
            if self.name:
                s = self.name.split('-')
                code = int(s[1])
                self.region_zone = code
        except:
            raise UserError('El nombre debe tener el siguiente formato NOMBRE-00')
    
    @api.constrains('guid_gaspar')
    def check_gaspar_id_validity(self):
        for price in self:
            if price.guid_gaspar and not re.match(utils._GUID_REGEX, price.guid_gaspar):
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
                response = utils.make_gaspar_request(url=url , method=method, params=price )
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

    # @api.constrains('guid_gaspar')
    # def check_gaspar_id_validity(self):
    #     for dc in self:
    #         if dc.guid_gaspar and not dc.guid_gaspar.match(utils._GUID_REGEX):
    #             raise UserError(_('Gaspar ID is invalid.'))


class GasparMedidor(models.Model):
    _name = 'gaspar.medidor'
    _description = 'Medidor Gaspar'

    name = fields.Char(string='Tag')
    company_id = fields.Many2one(comodel_name='res.company', string='Compañía', default=lambda self: self.env.company)
    
    idGaspar = fields.Char(string='Id Gaspar')
    application_type = fields.Selection(string='Tipo de aplicación', selection=[('AUTOTANQUE', 'AUTOTANQUE'), ('CARBURACION', 'CARBURACION'),])
    g4s_active = fields.Boolean(string='Activo')
    equipment_number = fields.Integer(string='Número de equipo')
    status = fields.Char(string='Estatus')
    link_key = fields.Char(string='Llave')
    comm_channel = fields.Char(string='Canal de comunicación')  
    cpu_serial_number = fields.Char(string='Número de serial CPU')
    

    def obtener_info_gaspar(self):
        for medidor in self:
            try:
                dc = utils.obtenerCentroDist(self.env)
                method = 'GET'
                baseUrl = self.env.company.gaspar_integracion_api
                url = baseUrl + '/corporateStructure/distCenter/' + dc.guid_gaspar + '/equipments/' + str(medidor.equipment_number)
                resp = utils.make_gaspar_request(url, method=method)
                if resp:
                    med = resp[0]
                    vals = {
                        'idGaspar': med['id'],
                        'application_type': med['applicationType'],
                        'g4s_active': med['active'],
                        'status': med['status'],
                        'link_key': str(med['linkKey']),
                        'comm_channel': med['commChannel'],
                        'cpu_serial_number': med['cpuSerialNumber'],
                        'name': med['tag']
                    }
                    medidor.update(vals)
            except Exception as e:
                raise UserError(_('No es posible guardar ruta en gaspar.  Error: %s' % e))

    def guardar_a_gaspar(self):
        for medidor in self:
            try:
                raise Exception('No implementado aún')                
            except Exception as e:
                raise UserError('No es posible guardar ruta en gaspar.  Error: %s' % e)
