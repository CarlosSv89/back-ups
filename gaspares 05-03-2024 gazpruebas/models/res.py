from email.policy import default
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import json
import urllib.request
from . import utils


class ResCompany(models.Model):
    _inherit = 'res.company'

    id_planta = fields.Char(string='Branch ID', readonly=False)


class ResPartner(models.Model):
    _inherit = 'res.partner'
    _sql_constraints = [('id_cliente_unique', 'UNIQUE(id_cliente, company_id)', 'El campo ID Cliente debe ser único.')]

    #TODO agregar dominio a la vista de arbol
    #Id de la planta
    id_planta = fields.Char(string='Id Planta', related='company_id.id_planta')
    #Id que asigna el chango
    id_cliente = fields.Char(string='ID Cliente')    
    #Id computado cuando se guarda el cliente
    id_cliente_completo = fields.Char(string='ID Combinado')
    scheme = fields.Integer(string='Esquema')
    #Id del cliente en el sistema de gaspar (GUID)
    id_cliente_gaspar = fields.Char(string='Gaspar ID')
    conciciones_pago_id = fields.Many2one(comodel_name='gaspar.condiciones.pago', string='Condiciones de pago gaspar')
    radio = fields.Integer(string='Radio')
    capacity = fields.Integer(string='Capacidad', default=300)
    
    
    #TODO Agregar campo de address id gaspar

    # @api.model
    # def create(self, vals):
    #     if 'id_cliente' in vals and self.env.company.id_planta:
    #         vals['id_cliente_completo'] = vals['id_cliente'] + self.env.company.id_planta.zfill(3)
    #     return super(ResPartner, self).create(vals)

    @api.onchange('id_cliente')
    def id_cliente_on_change(self):
        if self.id_cliente:
            self.id_cliente_completo = self.id_cliente + self.env.company.id_planta.zfill(3)


    @api.constrains('scheme')
    def check_scheme_validity(self):
        if not self.scheme:
            raise UserError(_('Scheme field is required'))
        if self.scheme < 1 or self.scheme > 100:
            raise UserError(_('Scheme must be between 1 and 100'))
    
    @api.constrains('capacity')
    def check_capacity_validity(self):
        if not self.capacity:
            raise UserError(_('Capacity field is required'))
        if self.capacity < 300 :
            raise UserError(_('Capacity cannot be less than 300'))

    def save_to_gaspar(self):
        try:
            for client in self:
                client._sync_to_gaspar()
                client._sync_reception_unit()
        except Exception as e:
            if isinstance(e, UserError):
                raise e
            raise Warning(_('Error saving to gaspar: %s') % e)

    def _sync_reception_unit(self):
        self.ensure_one()
        distCenters = self.env['gaspar.centro.distribucion'].search([])
        dc = None
        if not distCenters:
            raise UserError(_('There are not distribution centers, create one to continue.'))
        for distCenter in distCenters:
            dc = distCenter
            break
        receptionUnitList = {
            'receptionUnitList': [],
        }
        direccion = {
            'code': int(self.partner_id.id_cliente_completo),
            'customerCode': self.partner_id.id_cliente_completo,
            'scheme': self.partner_id.scheme,
            'capacity': self.partner_id.capacity if self.partner_id.capacity else 300,
            'descripction': self.partner_id.name,
            'discount': self.partner_id.discount,
            'priceRegionZone': self.precio_id.region_zone, 
            'productTypeId': 1,
            #'longitude': '-106.435162',# TODO regresar la selfa al subir a sh self.partner_id.longitude,
            'longitude': self.partner_id.partner_longitude,
            # 'latitude': '31.647179',# TODO regresar la selfa al subir a sh self.partner_id.latitude,
            'latitude': self.partner_id.partner_latitude,
            'radio': self.partner_id.radio,
            'generalPurpose1': '',# TODO Agregar si es credito o contado,
            'generalPurpose2': '',
            'street': self.partner_id.street,
            # 'externalNumber': '1',# TODO regresar la selfa al subir a sh self.partner_id.street_number,
            'externalNumber': self.partner_id.street_number,
            # 'internalNumber': '1',# TODO regresar la selfa al subir a sh self.partner_id.street_number,
            'internalNumber': self.partner_id.street_number2,
            # 'colony': 'Aeropuerto',# TODO regresar la selfa al subir a sh self.partner_id.I10n_mx_edi_colony,
            'colony': self.partner_id.l10n_mx_edi_colony,
            'zipCode': self.partner_id.zip,
            'state': self.partner_id.state_id.name,
            'municipality': self.partner_id.city_id.name or "",
            'distributionCenterId': dc.guid_gaspar
        }
        receptionUnitList['receptionUnitList'].append(direccion)
        url = self.env.company.gaspar_integracion_api + '/tomza/receptionUnits'
        response = utils.make_gaspar_request(url=url, method='POST', params=receptionUnitList)

    def _sync_to_gaspar(self):
        # TODO Verificar que el cliente exista en G4S
        # Si el cliente existe, entonces se hace una petición PUT,
        # Si el cliente no existe, se hace una petición POST
        self.ensure_one()
        customer = self._get_customer_json()
        customer['name'] = self.name
        customer['nationalFiscalIdentity'] = self.vat
        customer['email'] = self.email
        customer['sendNotifications'] = False
        customer['paymentConditionCode'] = self.conciciones_pago_id.gaspar_id
        customer['phoneNumber'] = self.phone.replace('+52', '').replace(' ', '')
        customer['phoneNumberType'] = 'FIXED'
        body = {
            'customersList': [customer]
        }
        url = self.env.company.gaspar_integracion_api + '/tomza/customers/'
        response = utils.make_gaspar_request(url, 'POST', body)

    def _get_customer_json(self):
        body = {
            'code': self.id_cliente_completo,
            'street': self.street,
            'externalNumber': '.',
            'internalNumber': self.street_number,
            'colony': self.I10n_mx_edi_colony,
            'zipCode': self.zip,
            'state': self.state_id.name,
            'municipality': self.city_id.name
        }
        return body


# class ResCountry(models.Model):
#     _inherit = 'res.country'

#     gaspar_id = fields.Integer(string='Gaspar Country ID')


# class ResCountryState(models.Model):
#     _inherit = 'res.country.state'

#     gaspar_id = fields.Integer(string='Gaspar State ID')


#     _inherit = 'res.city'

#     gaspar_id = fields.Integer(string='Gaspar State ID')
    
