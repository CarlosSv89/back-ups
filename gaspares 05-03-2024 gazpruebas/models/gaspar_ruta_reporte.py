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
    _name = 'gaspar.rep.ruta'
    _description = 'Reporte de ruta gaspar'

    name = fields.Char(string='Nombre', default='Nuevo')
    fecha_inicial = fields.Datetime(string='Fecha inicial')
    fecha_fin = fields.Datetime(string='Fecha final')
    pos_config_id = fields.Many2one(comodel_name='pos.config', string='Punto de venta')
    linea_ids = fields.One2many(comodel_name='gaspar.rep.ruta.linea', inverse_name='id_reporte', string='Líneas')
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

        vals['name'] = f'Ruta gaspar - {formatted_fecha_inicial} - {formatted_fecha_fin}'
        return super(ReporteServiciosGaspar, self).create(vals)


    @api.onchange('pos_config_id', 'fecha_inicial', 'fecha_fin')
    def obtener_eventos(self):
        try:
            if not self.fecha_inicial or not self.fecha_fin:
                return

            if not self.pos_config_id:
                return
            if not self.pos_config_id.distribution_point_name:
                raise UserError('El punto de venta no tiene configurado el servicio de gaspar')

            self.linea_ids = [(5, 0, 0)]  # Limpiar líneas existentes antes de agregar nuevas

            params = {
                'serverName': self.env.company.gaspar_server.external_id,
                'distributionPointName': self.pos_config_id.distribution_point_name
            }

            gasparTz = pytz.timezone(self.env.company.zona_horaria)
            if not gasparTz:
                raise UserError('Asigna una zona horaria para el servidor gaspar para continuar')

            fechaInicial = pytz.utc.localize(self.fecha_inicial).astimezone(gasparTz)
            fechaFinal = pytz.utc.localize(self.fecha_fin).astimezone(gasparTz)
            params['initDate'] = fechaInicial.strftime('%Y-%m-%dT%H:%M:%S')
            params['endDate'] = fechaFinal.strftime('%Y-%m-%dT%H:%M:%S')

            url = self.env['ir.config_parameter'].get_param('pos_route_config.gas_api_url') + 'ruta'
            req = urllib.request.Request(url, data=json.dumps(params).encode('utf8'),
                                         headers={'content-type': 'application/json'}, method='GET')
            decodedResponse = urllib.request.urlopen(req).read().decode('utf8')
            response = json.loads(decodedResponse)

            if response['code'] in (400, 500):
                raise UserError(response['message'])

            if response['result']:
                for service in response['result']:
                    linea = {
                        'id_equipo': service['idequipo'],
                        'tag': service['tag'],
                        'consecutivo': service['consecutive'],
                        'fecha': service['point_timestamp'],
                        'longitud': service['longitude'],
                        'latitud': service['latitude'],
                        'radio_error': service['radio_error'],
                        'curso': service['course'],
                        'velocidad': service['velocity']
                    }
                    self.linea_ids = [(0, 0, linea)]  # Agregar la línea a la lista de líneas
        except Exception as e:
            if isinstance(e, UserError):
                raise e
            _logger.error(e)
            raise UserError("Error en el servidor, intente mas tarde")


class ReporteSeviciosGasparLineas(models.Model):
    _name = 'gaspar.rep.ruta.linea'
    _description = 'Líneas de reporte de ruta gaspar'

    id_reporte = fields.Many2one(comodel_name='gaspar.rep.ruta', string='Reporte')
    id_equipo = fields.Char(string='ID Equipo')
    tag = fields.Char(string='Tag')
    consecutivo = fields.Integer(string='Consecutivo')
    fecha = fields.Datetime(string='Fecha')
    longitud = fields.Float(string='Longitud', digits=(10, 6))
    latitud = fields.Float(string='Latitud', digits=(10, 6))
    radio_error = fields.Integer(string='Error de radio')
    curso = fields.Integer(string='Curso')
    velocidad = fields.Float(string='Velocidad', digits=(10, 6))



class ReporteVentasGaspar(models.Model):
    _name = 'report.gaspar.rep.ruta'
    _description = 'Reporte de ruta gaspar'
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


            sheet.write(3, 1, 'ID Equipo', format_header)
            sheet.write(3, 2, 'Tag', format_header)
            sheet.write(3, 3, 'Consecutivo', format_header)
            sheet.write(3, 4, 'Fecha', format_header)
            sheet.write(3, 5, 'Longitud', format_header)
            sheet.write(3, 6, 'Latitud', format_header)
            sheet.write(3, 7, 'Radio error', format_header)
            sheet.write(3, 8, 'Curso', format_header)
            sheet.write(3, 9, 'Velocidad', format_header)
            row = 4

            format_cell = workbook.add_format({'bold': True, 'bg_color': '#92D050'})
            date_format = workbook.add_format(
                {'font_color': 'black', 'bg_color': 'white', 'border': True, 'border_color': '#D3D3D3',
                 'num_format': 'dd/mm/yy hh:mm:ss', 'align': 'center'})
            cell = workbook.add_format(
                {'font_color': 'black', 'bg_color': 'white', 'border': True, 'border_color': '#D3D3D3',
                 'align': 'left'})
            for linea in evento.linea_ids:
                sheet.write(row, 1, linea.id_equipo)
                sheet.write(row, 2, linea.tag)
                sheet.write(row, 3, linea.consecutivo)
                sheet.write(row, 4, linea.fecha, date_format)
                sheet.write(row, 5, linea.longitud)
                sheet.write(row, 6, linea.latitud)
                sheet.write(row, 7, linea.radio_error)
                sheet.write(row, 8, linea.curso)
                sheet.write(row, 9, linea.velocidad)
                row += 1

