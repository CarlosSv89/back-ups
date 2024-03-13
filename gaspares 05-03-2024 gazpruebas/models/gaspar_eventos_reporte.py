from datetime import datetime, timedelta
from pytz import timezone
import json
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import logging
import pytz
import urllib.request

_logger = logging.getLogger(__name__)


class ReporteServiciosGaspar(models.Model):
    _name = 'gaspar.rep.eventos'
    _description = 'Reporte de eventos gaspar'

    name = fields.Char(string='Nombre', default='Nuevo')
    fecha_inicial = fields.Datetime(string='Fecha inicial')
    fecha_fin = fields.Datetime(string='Fecha final')
    all_pos = fields.Boolean(string='Seleccionar todos los puntos de venta', default=False)
    pos_config_id = fields.Many2one(comodel_name='pos.config', string='Punto de venta')
    linea_ids = fields.One2many(comodel_name='gaspar.rep.eventos.linea', inverse_name='reporte_id', string='Líneas')
    company_id = fields.Many2one(comodel_name='res.company', required=True, default=lambda self: self.env.company)

    @api.model
    def create(self, vals):
        fecha_inicial = fields.Datetime.to_datetime(vals.get('fecha_inicial'))
        fecha_fin = fields.Datetime.to_datetime(vals.get('fecha_fin'))

        # Convertir a la zona horaria del servidor Gaspar
        gasparTz = pytz.timezone(self.env.company.zona_horaria)
        if not gasparTz:
            raise UserError('Asigna una zona horaria para el servidor Gaspar para continuar')

        fecha_inicial = fecha_inicial.astimezone(gasparTz)
        fecha_fin = fecha_fin.astimezone(gasparTz)

        # Restar una hora a las fechas
        fecha_inicial -= timedelta(hours=1)
        fecha_fin -= timedelta(hours=1)

        # Formatear las fechas
        formatted_fecha_inicial = fecha_inicial.strftime('%Y-%m-%d %H:%M:%S')
        formatted_fecha_fin = fecha_fin.strftime('%Y-%m-%d %H:%M:%S')

        vals['name'] = f'Eventod gaspar - {formatted_fecha_inicial} - {formatted_fecha_fin}'
        return super(ReporteServiciosGaspar, self).create(vals)


    @api.onchange('pos_config_id', 'fecha_inicial', 'fecha_fin', 'all_pos')
    def obtener_eventos(self):
        try:
            if not self.fecha_inicial or not self.fecha_fin:
                return

            if not self.all_pos and not self.pos_config_id:
                return
            pos_configs = []
            if not self.all_pos and self.pos_config_id:
                if not self.pos_config_id.distribution_point_name:
                    raise UserError('El punto de venta no tiene configurado el servicio de gaspar')
            else:
                pos_configs = self.env['pos.config'].search([('distribution_point_name', '!=', False)])

            self.linea_ids = [(5, 0, 0)]  # Limpiar líneas existentes antes de agregar nuevas

            params = {
                'serverName': self.env.company.gaspar_server.external_id,
            }
            if not self.all_pos:
                params['distributionPointNames'] = [self.pos_config_id.distribution_point_name]
            else:
                params['distributionPointNames'] = [x.distribution_point_name for x in pos_configs]

            gasparTz = pytz.timezone(self.env.company.zona_horaria)
            if not gasparTz:
                raise UserError('Asigna una zona horaria para el servidor gaspar para continuar')

            fechaInicial = pytz.utc.localize(self.fecha_inicial).astimezone(gasparTz)
            fechaFinal = pytz.utc.localize(self.fecha_fin).astimezone(gasparTz)
            params['initDate'] = fechaInicial.strftime('%Y-%m-%dT%H:%M:%S')
            params['endDate'] = fechaFinal.strftime('%Y-%m-%dT%H:%M:%S')

            url = self.env['ir.config_parameter'].get_param('pos_route_config.gas_api_url') + 'event'
            req = urllib.request.Request(url, data=json.dumps(params).encode('utf8'),
                                         headers={'content-type': 'application/json'}, method='GET')
            decodedResponse = urllib.request.urlopen(req).read().decode('utf8')
            response = json.loads(decodedResponse)

            if response['code'] in (400, 500):
                raise UserError(response['message'])

            if response['result']:
                for service in response['result']:
                    linea = {
                        'id_medidor': service['idmedidor'],
                        'equipment_number': service['equipment_number'],
                        'tag': service['tag'],
                        'id_evento': service['id'],
                        'consecutivo': service['consecutive'],
                        'fecha': service['date'],#datetime.strptime(service['date'][:-6], '%Y-%m-%dT%H:%M:%S'),
                        'field1': service['field1'],
                        'field2': service['field2'],
                        'hardware_module_id': service['hardware_module_id'],
                        'module_direction': service['module_direction'],
                        'id_tipo_evento': service['event_type_id'],
                        'descripcion': service['description'],
                        'longitud': service['longitude'],
                        'latitud': service['latitude'],
                        'altitud': service['altitude'],
                        'error_radio': service['radio_error'],
                        'condiciones_operacion': service['operation_conditions'] if service['operation_conditions'] else '',
                        'id_equipo': service['equipment_id'],
                        'id_corte': service['cut_id'],
                        'id_empleado': service['employee_id'] if service['employee_id'] else '',
                        'fecha_insercion': service['insertion_timestamp'],#datetime.strptime(service['insertion_timestamp'][:-9], '%Y-%m-%dT%H:%M:%S'),
                        'tag_equipo': service['equipment_tag'],
                        'numero_equipo': service['equipment_number'],
                        'tipo_equipo': service['equipment_application_type'],
                        'nombre_punto_distribucion': service['distribution_point_name'],
                        'nombre_centro_distribucion': service['distribution_center_name'],
                        'nombre_region': service['region_name'],
                        'nombre_empresa': service['company_name'],
                        'lost_mark_timestamp': service['lost_mark_timestamp'],#datetime.strptime(service['lost_mark_timestamp'][:-9], '%Y-%m-%dT%H:%M:%S') if service['lost_mark_timestamp'] else '',
                        'severidad': service['severity'],
                        'exportado': service['exported'],
                        #'contador': service['counter'] if service['counter'] else '',
                        #'tipo_usuario': service['user_type_id'],
                        #'id_cpu': service['cpu_id']
                    }
                    self.linea_ids = [(0, 0, linea)]  # Agregar la línea a la lista de líneas
        except Exception as e:
            if isinstance(e, UserError):
                raise e
            _logger.error(e)
            raise UserError("Error en el servidor, intente mas tarde")


class ReporteSeviciosGasparLineas(models.Model):
    _name = 'gaspar.rep.eventos.linea'
    _description = 'Líneas de reporte de servicios gaspar'

    reporte_id = fields.Many2one(comodel_name='gaspar.rep.eventos', string='Reporte')
    id_medidor = fields.Char(string='ID medidor')
    equipment_number = fields.Char(string='Número de equipo')
    tag = fields.Char(string='Tag')
    id_evento = fields.Char(string='ID evento')
    consecutivo = fields.Integer(string='Consecutivo')
    fecha = fields.Datetime(string='Fecha')
    field1 = fields.Char(string='Field1')
    field2 = fields.Char(string='Field2')
    hardware_module_id = fields.Integer(string='ID módulo de hardware')
    module_direction = fields.Integer(string='Dirección del módulo')
    id_tipo_evento = fields.Integer(string='ID tipo de evento')
    descripcion = fields.Char(string='Descripción')
    longitud = fields.Float(string='Longitud')
    latitud = fields.Float(string='Latitud')
    altitud = fields.Float(string='Altitud')
    error_radio = fields.Integer(string='Error de radio')
    condiciones_operacion = fields.Char(string='Condiciones de operación')
    id_equipo = fields.Char(string='ID equipo')
    id_corte = fields.Char(string='ID corte')
    id_empleado = fields.Char(string='ID empleado')
    fecha_insercion = fields.Datetime(string='Fecha de inserción')
    tag_equipo = fields.Char(string='Tag de equipo')
    numero_equipo = fields.Integer(string='Número de equipo')
    tipo_equipo = fields.Char(string='Tipo de equipo')
    nombre_punto_distribucion = fields.Char(string='Nombre del punto de distribución')
    nombre_centro_distribucion = fields.Char(string='Nombre del centro de distribución')
    nombre_region = fields.Char(string='Nombre de la región')
    nombre_empresa = fields.Char(string='Nombre de la empresa')
    lost_mark_timestamp = fields.Datetime(string='Marca de tiempo perdida')
    severidad = fields.Integer(string='Severidad')
    exportado = fields.Boolean(string='Exportado')


class ReporteVentasGaspar(models.Model):
    _name = 'report.gaspar.rep.eventos'
    _description = 'Reporte de servicios gaspar'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, eventos):
        for evento in eventos:
            sheet = workbook.add_worksheet(evento.name)
            sheet.write(0, 0, evento.name, workbook.add_format({'bold': True}))
            format_header = workbook.add_format({'bold': True, 'bg_color': '#222A35', 'font_color': 'white'})
            sheet.set_column(0, 0, 30)
            sheet.set_column(1, 1, 30)
            sheet.set_column(2, 2, 20)
            sheet.set_column(3, 3, 30)
            sheet.set_column(4, 4, 30)
            sheet.set_column(5, 5, 30)
            sheet.set_column(6, 6, 30)
            sheet.set_column(7, 7, 30)
            sheet.set_column(8, 8, 30)
            sheet.set_column(9, 9, 30)
            sheet.set_column(10, 10, 30)
            sheet.set_column(11, 11, 30)
            sheet.set_column(12, 12, 30)
            sheet.set_column(13, 13, 30)
            sheet.set_column(14, 14, 30)
            sheet.set_column(15, 15, 30)
            sheet.set_column(16, 16, 30)
            sheet.set_column(17, 17, 30)
            sheet.set_column(18, 18, 30)
            sheet.set_column(19, 19, 30)
            sheet.set_column(20, 20, 30)
            sheet.set_column(21, 21, 30)
            sheet.set_column(22, 22, 30)
            sheet.set_column(23, 23, 30)
            sheet.set_column(24, 24, 30)
            sheet.set_column(25, 25, 30)
            sheet.set_column(26, 26, 30)
            sheet.set_column(27, 27, 30)
            sheet.set_column(28, 28, 30)
            sheet.set_column(29, 29, 30)
            sheet.set_column(30, 30, 30)


            sheet.write(3, 1, 'Id medidor', format_header)
            sheet.write(3, 2, '# Equipo', format_header)
            sheet.write(3, 3, 'Tag', format_header)
            sheet.write(3, 4, 'Id evento', format_header)
            sheet.write(3, 5, 'Fecha/Hora', format_header)
            sheet.write(3, 6, 'Consecutivo', format_header)
            sheet.write(3, 7, 'Fecha', format_header)
            sheet.write(3, 8, 'Campo 1', format_header)
            sheet.write(3, 9, 'Campo 2', format_header)
            sheet.write(3, 10, 'Id Módulo', format_header)
            sheet.write(3, 11, 'Dirección módulo', format_header)
            sheet.write(3, 12, 'ID tipo evento', format_header)
            sheet.write(3, 13, 'Descripcion', format_header)
            sheet.write(3, 14, 'Longitud', format_header)
            sheet.write(3, 15, 'Latitud', format_header)
            sheet.write(3, 16, 'Altitud', format_header)
            sheet.write(3, 17, 'Error de radio', format_header)
            sheet.write(3, 18, 'Condiciones de operación', format_header)
            sheet.write(3, 19, 'ID equipo', format_header)
            sheet.write(3, 20, 'ID corte', format_header)
            sheet.write(3, 21, 'ID empleado', format_header)
            sheet.write(3, 22, 'Fecha inserción', format_header)
            sheet.write(3, 23, 'Tag equipo', format_header)
            sheet.write(3, 24, 'Punto de distribución', format_header)
            sheet.write(3, 25, 'Centro de distribución', format_header)
            sheet.write(3, 26, 'Región', format_header)
            sheet.write(3, 27, 'Nombre empresa', format_header)
            sheet.write(3, 28, 'Marca de tiempo perdida', format_header)
            sheet.write(3, 29, 'Severidad', format_header)
            sheet.write(3, 30, 'Exportado', format_header)

            row = 4

            format_cell = workbook.add_format({'bold': True, 'bg_color': '#92D050'})
            date_format = workbook.add_format(
                {'font_color': 'black', 'bg_color': 'white', 'border': True, 'border_color': '#D3D3D3',
                 'num_format': 'dd/mm/yy hh:mm:ss', 'align': 'center'})
            cell = workbook.add_format(
                {'font_color': 'black', 'bg_color': 'white', 'border': True, 'border_color': '#D3D3D3',
                 'align': 'left'})
            for linea in evento.linea_ids:
                sheet.write(row, 1, linea.id_medidor)  # 1
                sheet.write(row, 2, linea.equipment_number)  # 2
                sheet.write(row, 3, linea.tag)  # 3
                sheet.write(row, 4, linea.id_evento)  # 4
                sheet.write(row, 5, linea.consecutivo)  # 5
                sheet.write(row, 6, linea.fecha, date_format)  # 6 suma
                sheet.write(row, 7, linea.field1)  # 7
                sheet.write(row, 8, linea.field2)  # 8 suma
                sheet.write(row, 9, linea.hardware_module_id)  # 9 suma
                sheet.write(row, 10, linea.module_direction)  # 10
                sheet.write(row, 11, linea.id_tipo_evento)  # 11
                sheet.write(row, 12, linea.descripcion)  # 12
                sheet.write(row, 13, linea.longitud)  # 13
                sheet.write(row, 14, linea.latitud)  # 14
                sheet.write(row, 15, linea.altitud)  # 15
                sheet.write(row, 16, linea.error_radio)  # 16 suma
                sheet.write(row, 17, linea.condiciones_operacion)
                sheet.write(row, 18, linea.id_equipo)
                sheet.write(row, 19, linea.id_corte)
                sheet.write(row, 20, linea.id_empleado)
                sheet.write(row, 21, linea.fecha_insercion)
                sheet.write(row, 22, linea.tag_equipo)
                sheet.write(row, 23, linea.numero_equipo)
                sheet.write(row, 24, linea.tipo_equipo)
                sheet.write(row, 25, linea.nombre_punto_distribucion)
                sheet.write(row, 26, linea.nombre_centro_distribucion)
                sheet.write(row, 27, linea.nombre_region)
                sheet.write(row, 28, linea.nombre_empresa)
                sheet.write(row, 29, linea.lost_mark_timestamp)
                sheet.write(row, 30, linea.severidad)
                sheet.write(row, 31, linea.exportado)
                row += 1

