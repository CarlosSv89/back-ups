from email.mime import base
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from . import utils


class RutaClientes(models.Model):
    _inherit = 'rutas.clientes'

    id_planta = fields.Char(string='Branch ID', default=lambda self: self.env.company.id_planta)
    medidor_id = fields.Many2one(comodel_name='gaspar.medidor', string='Medidor G4S')
    config_id = fields.Many2one(comodel_name='pos.config', string='Punto de venta')
            
    
    # @api.model
    # def create(self, vals):
    #     idPlanta = vals['id_planta'].zfill(3)
    #     code = str(vals['id_ruta']) + idPlanta
    #     vals['code'] = code
    #     return super(RutaClientes, self).create(vals)

    
    # def write(self, vals):
    #     idPlanta = self.id_planta.zfill(3)
    #     if 'id_ruta' in vals:
    #         code = str(vals['id_ruta']) + idPlanta
    #         vals['code'] = code
    #     return super(RutaClientes, self).write(vals)

    @api.onchange('id_ruta')
    def id_ruta_on_change(self):
        idPlanta = self.id_planta.zfill(3)
        if self.id_ruta:
            code = str(self.id_ruta) + idPlanta
            self.code = code


    @api.constrains('id_planta')
    def _check_id_planta(self):
        for ruta in self:
            if not ruta.id_planta:
                raise UserError(_('The branch ID is required. Configure this value at the company form.'))


    # Pasos para crear una ruta
    # 1. Crear una ruta en gaspar o actualizar (vaciar la ruta)
    # 2. Actualizar la lista de receptionUnits de gaspar (sucursales de clientes)
    # 3. Actualizar la lista de clientes de gaspar (clientes de la ruta)
    def sync_to_gaspar(self):
        # TODO Sincronizar ruta y equipo (medidor)
        # asignarRutaEquipo
        for ruta in self:
            try:
                distCenters = self.env['gaspar.centro.distribucion'].search([])
                dc = None
                if not distCenters:
                    raise UserError(_('There are not distribution centers, create one to continue.'))
                for distCenter in distCenters:
                    dc = distCenter
                    break
                method = 'PUT'
                baseUrl = self.env.company.gaspar_integracion_api
                url = baseUrl + '/catalogs/routes/' + ruta.code
                body = {
                    'code': ruta.code,
                    'routeName': ruta.name,
                    'distributionCenterId': dc.guid_gaspar,
                    'receptionUnitsIds': [],
                }
                # 1. Crear una ruta en gaspar o actualizar (vaciar la ruta)
                # if ruta.guid_gaspar:
                #     method = 'PUT'
                #     url = url + '/' + ruta.code
                response = utils.make_gaspar_request(url=url , method=method, params=body)
                #TODO Verificar si el resultado de la respuesta es correcto

                # 2. Actualizar la lista de receptionUnits de gaspar (sucursales de clientes)
                receptionUnitList = {
                    'receptionUnitList': [],
                }
                customerscode = []
                customerscode.append(ruta.clientes_lines_ids.mapped('id_cliente_completo'))
                # for line in ruta.clientes_lines_ids:
                #     customerscode.append(line.partner_id.id_cliente_completo)

                # 3. Actualizar la lista de clientes de gaspar (clientes de la ruta)
                body = {
                    'routeCode': ruta.code,
                    'customersCodes': customerscode,
                }
                url = baseUrl + '/catalogs/routes/addCustomers'
                response = utils.make_gaspar_request(url=url, method='POST', params=body)
                #TODO Verificar si el resultado de la respuesta es correcto

            except Exception as e:
                raise UserError(_('No es posible guardar ruta en gaspar. </br> Error: %s' % e))

    def asignar_ruta_medidor(self):
        # TODO 1 Verificar que la ruta no haya sido asignado a otro medidor
        # TODO 2 Verificar que la ruta no haya sido asignada a otro punto de venta
        # TODO Asignar ruta con medidor en gaspares
        for ruta in self:
            try:
                if not ruta.config_id:
                    raise UserError('Debes asignar un punto de venta a la ruta para poder sincronizar con G4S')
                if not ruta.medidor_id:
                    raise UserError('Debes asignar un medidor disponible a la ruta para poder continuar')
                rutas = self.env['rutas.clientes'].search([('medidor_id', '=', ruta.medidor_id.id)])
                if rutas:
                    for r in rutas:
                        if not r.id == ruta.id:
                            raise UserError('El medidor %s ya ha sido asignado a otra ruta. No es posible asignarlo a una ruta nueva' % ruta.medidor_id.name)
                configs = self.env['pos.config'].search([('ruta_id', '=', ruta.id)])
                if configs:
                    for config in configs:
                        if not config.id == ruta.config_id.id:
                            raise UserError('La ruta ya ha sido asignada a otro punto de venta, selecciona otro punto de venta que no tenga una ruta asignada')

                body = {
                    'routeCode': ruta.code,
                    'equipmentCode': ruta.medidor_id.equipment_number
                }
                baseUrl = self.env.company.gaspar_integracion_api
                url = baseUrl + '/catalogs/routes/assign'                
                resp = utils.make_gaspar_request(url, 'POST', body)
                ruta.config_id.update({'ruta_id': ruta.id})
            except Exception as e:
                raise UserError('No es posible guardar ruta en gaspar. Error: %s' % e)