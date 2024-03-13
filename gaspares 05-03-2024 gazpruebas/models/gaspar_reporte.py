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
    _name = 'gaspar.rep.servicios'
    _description = 'Reporte de servicios gaspar'

    name = fields.Char(string='Nombre', default='Nuevo')
    fecha_inicial = fields.Datetime(string='Fecha inicial')
    fecha_fin = fields.Datetime(string='Fecha final')
    all_pos = fields.Boolean(string='Seleccionar todos los puntos de venta', default=False)
    pos_config_id = fields.Many2one(comodel_name='pos.config', string='Punto de venta')
    linea_ids = fields.One2many(comodel_name='gaspar.rep.servicios.linea', inverse_name='reporte_id', string='Líneas')
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

        vals['name'] = f'Servicios gaspar - {formatted_fecha_inicial} - {formatted_fecha_fin}'
        return super(ReporteServiciosGaspar, self).create(vals)
    
    def _get_time_zone(self):
        res_users_obj = self.env['res.users']
        userstz = res_users_obj.browse(self._uid).tz
        a = 0
        if userstz:
            hours = timezone(userstz)
            fmt = '%Y-%m-%d %H:%M:%S %Z%z'
            now = datetime.now()
            loc_dt = hours.localize(datetime(now.year, now.month, now.day,
                                             now.hour, now.minute, now.second))
            timezone_loc = (loc_dt.strftime(fmt))
            diff_timezone_original = timezone_loc[-5:-2]
            timezone_original = int(diff_timezone_original)
            s = str(datetime.now(timezone(userstz)))
            s = s[-6:-3]
            timezone_present = int(s)*-1
            a = timezone_original + ((
                timezone_present + timezone_original)*-1)
        return a

    @api.onchange('pos_config_id', 'fecha_inicial', 'fecha_fin', 'all_pos')
    def obtener_servicios(self):
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
                params['distributionPointName'] = self.pos_config_id.distribution_point_name
            else:
                params['distributionPointNames'] = [x.distribution_point_name for x in pos_configs]

            gasparTz = pytz.timezone(self.env.company.zona_horaria)
            if not gasparTz:
                raise UserError('Asigna una zona horaria para el servidor gaspar para continuar')

            fechaInicial = pytz.utc.localize(self.fecha_inicial).astimezone(gasparTz)
            fechaFinal = pytz.utc.localize(self.fecha_fin).astimezone(gasparTz)
            params['initDate'] = fechaInicial.strftime('%Y-%m-%dT%H:%M:%S')
            params['endDate'] = fechaFinal.strftime('%Y-%m-%dT%H:%M:%S')

            url = self.env['ir.config_parameter'].get_param('pos_route_config.gas_api_url') + 'sale/customService'
            req = urllib.request.Request(url, data=json.dumps(params).encode('utf8'), headers={'content-type': 'application/json'}, method='GET')
            decodedResponse = urllib.request.urlopen(req).read().decode('utf8')
            response = json.loads(decodedResponse)

            if response['code'] in (400, 500):
                raise UserError(response['message'])

            if response['result']:
                for service in response['result']:
                    linea = {
                        'id_venta': service['saleid'],
                        'id_medidor': service['equipmentid'],
                        'tag': service['tag'],  # Asignar el valor del tag aquí
                        'id_cliente': service['customerid'],
                        'nombre_cliente': service['customername'],
                        'id_negocio': service['receptionunitid'],
                        'folio': service['folio'],
                        'fecha_inicio': datetime.strptime(service['startdate'][:-6], '%Y-%m-%dT%H:%M:%S'),
                        'fecha_final': datetime.strptime(service['enddate'][:-6], '%Y-%m-%dT%H:%M:%S'),
                        'forma_pago': service['paymenttype'],
                        'precio': service['price'],
                        'volumen': service['volume'],
                        'masa': service['mass'],
                        'descuento': service['discount'],
                        'importe': service['amount'],
                        'alarma': service['alarms'],
                        'condiciones': service['conditions'],
                        'sector': service['sector'],
                        'densidad': service['density'],
                        'temperatura': service['temperature'],
                        'longitud': service['longitude'],
                        'latitud': service['latitude'],
                        'radio': service['radio'],
                        'num_equipo': service['equipmentnumber'],
                        'totalizador': service['totalizer'],
                        'totalizador_masa': service['totalizermass']
                    }
                    self.linea_ids = [(0, 0, linea)]  # Agregar la línea a la lista de líneas
        except Exception as e:
            if isinstance(e, UserError):
                raise e
            _logger.error(e)
            raise UserError("Error en el servidor, intente mas tarde")





class ReporteSeviciosGasparLineas(models.Model):
    _name = 'gaspar.rep.servicios.linea'
    _description = 'Líneas de reporte de servicios gaspar'

    reporte_id = fields.Many2one(comodel_name='gaspar.rep.servicios', string='Reporte')
    id_venta = fields.Char(string='ID venta')
    id_medidor = fields.Char(string='ID medidor')
    tag = fields.Char(string='Tag')
    id_cliente = fields.Char(string='ID cliente')
    nombre_cliente = fields.Char(string='Cliente')
    id_negocio = fields.Integer(string='ID negocio')
    folio = fields.Char(string='Folio')
    fecha_inicio = fields.Datetime(string='Fecha inicio')
    fecha_final = fields.Datetime(string='Fecha final')
    forma_pago = fields.Char(string='Forma de pago')
    precio = fields.Float(string='Precio', digits=(16, 2))
    volumen = fields.Float(string='Volumen', digits=(16, 2))
    masa = fields.Float(string='Masa', digits=(16, 2))
    descuento = fields.Float(string='Descuento', digits=(16, 2))
    importe = fields.Float(string='Importe', digits=(16, 2))
    alarma = fields.Char(string='Alarma')
    condiciones = fields.Float(string='Condiciones', digits=(16, 2))
    sector = fields.Integer(string='Sector')
    densidad = fields.Integer(string='Densidad')
    temperatura = fields.Integer(string='Temperatura')
    longitud = fields.Float(string='Longitud', digits=(10, 6))
    latitud = fields.Float(string='Latitud', digits=(10, 6))
    radio = fields.Integer(string='Radio')
    num_equipo = fields.Integer(string='Número de equipo')
    totalizador = fields.Float(string='Totalizador', digits=(16, 2))
    totalizador_masa = fields.Float(string='Totalizador masa', digits=(16, 2))


class ReporteVentasGaspar(models.Model):
    _name = 'report.gaspar.rep.servicios'
    _description = 'Reporte de servicios gaspar'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, servicios):
        for servicio in servicios:
            sheet = workbook.add_worksheet(servicio.name)
            sheet.write(0, 0, servicio.name, workbook.add_format({'bold': True}))
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
            
            
            sheet.write(3, 1, 'Punto de venta', format_header)
            sheet.write(3, 2, 'ID cliente', format_header)
            sheet.write(3, 3, 'Cliente', format_header)
            sheet.write(3, 4, '# Servicio', format_header)
            sheet.write(3, 5, 'Fecha/Hora', format_header)
            sheet.write(3, 6, 'Volumen', format_header)
            sheet.write(3, 7, 'Precio', format_header)
            sheet.write(3, 8, 'Descuento', format_header)
            sheet.write(3, 9, 'Importe', format_header)
            sheet.write(3, 10, 'Longitud', format_header)
            sheet.write(3, 11, 'Latitud', format_header)
            sheet.write(3, 12, 'Alarma', format_header)
            sheet.write(3, 13, 'Sector', format_header)
            sheet.write(3, 14, 'Pago', format_header)
            sheet.write(3, 15, 'Recibido', format_header)
            sheet.write(3, 16, 'Totalizador', format_header)
            sheet.write(3, 17, 'Densidad', format_header)
            row = 4
            servicio_total = 0
            volumen_total = 0.00
            descuento_total = 0.00
            importe_total = 0.00
            totalizador_total = 0.00
            densidad_total = 0.00

            format_cell = workbook.add_format({'bold': True, 'bg_color': '#92D050'})
            date_format = workbook.add_format({'font_color': 'black', 'bg_color': 'white','border':True,'border_color': '#D3D3D3', 'num_format': 'dd/mm/yy hh:mm:ss', 'align': 'center'})
            cell = workbook.add_format({'font_color': 'black', 'bg_color': 'white','border':True,'border_color': '#D3D3D3', 'align': 'left'})
            for linea in servicio.linea_ids:
                sheet.write(row, 1, linea.tag)#1
                sheet.write(row, 2, linea.id_cliente)#2
                sheet.write(row, 3, linea.nombre_cliente)#3
                sheet.write(row, 4, linea.folio)#4
                sheet.write(row, 5, linea.fecha_inicio, date_format)#5
                sheet.write(row, 6, linea.volumen)#6 suma
                sheet.write(row, 7, linea.precio)#7
                sheet.write(row, 8, linea.descuento)#8 suma
                sheet.write(row, 9, linea.importe)#9 suma
                sheet.write(row, 10, linea.longitud)#10
                sheet.write(row, 11, linea.latitud)#11
                sheet.write(row, 12, linea.alarma)#12
                sheet.write(row, 13, linea.sector)#13
                sheet.write(row, 14, linea.forma_pago)#14
                sheet.write(row, 15, linea.fecha_final, date_format)#15
                sheet.write(row, 16, linea.totalizador)#16 suma
                sheet.write(row, 17, linea.densidad)#17 suma
                servicio_total = servicio_total + 1
                volumen_total = volumen_total + linea.volumen
                descuento_total = descuento_total + linea.descuento
                importe_total = importe_total + linea.importe
                totalizador_total = totalizador_total + linea.totalizador
                densidad_total =  densidad_total + linea.densidad
                row += 1
            sheet.write(row, 0, "TOTAL", format_header)
            sheet.write(row, 4, servicio_total, cell)#4
            sheet.write(row, 6, volumen_total)#6 suma
            sheet.write(row, 8, descuento_total)#8 suma
            sheet.write(row, 9, importe_total)#9 suma
            sheet.write(row, 16, totalizador_total)#16 suma
            sheet.write(row, 17, densidad_total)#17 suma

