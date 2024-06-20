import string
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError
from pytz import timezone
import logging

_logger = logging.getLogger(__name__)

class libro_ingresos(models.Model):  # primera clase -----------------------------------------------------
    _name = 'libro_ingresos.libro'
    _description = 'Libro de ingresos'

    # Llaves
    linea_libro_ids = fields.One2many(comodel_name='libro_ingresos.linea_libro', inverse_name='libro_id', string='Líneas de libro ingresos')  # LLAVE DE ORDENES
    company_id = fields.Many2one("res.company", string='Compañía', ondelete='restrict', default=lambda self: self.env.company)
    planta = fields.Many2one("res.company", string='Planta')  # atributo planta
    responsable = fields.Many2one("res.users", string="Responsable", domain="[('groups_id.name', '=', 'Liquidaciones'),('company_ids','=?',company_id),('x_studio_liquidaciones_1','=',True)]")

    # atributos de la clase
    name = fields.Char(string='Nombre', default='Nuevo')
    fecha_libro = fields.Date(string='Fecha inicial')
    fecha_final = fields.Date(string='Fecha final')
    saldo_inicial = fields.Float(string='Saldo inicial', default=0.00)
    saldo_final = fields.Float(string='Saldo final', compute='_compute_saldo_final', store=True)

    # aquí comienzan los controles para manejar las fechas --------------------------------------------------------------------------------------
    @api.constrains('fecha_libro')
    def _check_unique_fecha_libro(self):
        if self.fecha_libro:
            for record in self:
                if self.search([('fecha_libro', '=', record.fecha_libro), ('planta.name', '=', record.planta.name), ('id', '!=', record.id)], limit=1):
                    raise ValidationError("Ya existe un libro de ingresos con esta fecha y planta.")

    @api.depends('linea_libro_ids.saldo')
    def _compute_saldo_final(self):
        for libro in self:
            if libro.linea_libro_ids:
                libro.saldo_final = libro.linea_libro_ids[-1].saldo
            else:
                libro.saldo_final = libro.saldo_inicial

    # Aquí comienzan los controles para manejar las fechas
    @api.model
    def create(self, vals):
        vals['name'] = f"Libro de ingresos : {vals['fecha_libro']} al {vals['fecha_final']}"   # titulo
        fecha_libro = datetime.strptime(vals['fecha_libro'], '%Y-%m-%d').date()
        planta_id = vals['planta']
        fecha_anterior = fecha_libro - timedelta(days=1)

        registro_anterior = self.search([('fecha_libro', '=', fecha_anterior), ('planta', '=', planta_id)], limit=1)
        if registro_anterior:
            vals['saldo_inicial'] = registro_anterior.saldo_final
        return super(libro_ingresos, self).create(vals)

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

    @api.onchange('fecha_libro', 'fecha_final', 'planta', 'saldo_inicial')
    def _calcular_valores(self):
        for libro in self:
            if libro.fecha_libro and libro.fecha_final and libro.planta:
                init_date = libro.fecha_libro
                end_date = libro.fecha_final
                time_zone = self._get_time_zone()

                # Buscar registro del día anterior
                fecha_anterior = init_date - timedelta(days=1)
                registro_anterior = self.env['libro_ingresos.libro'].search(
                    [('fecha_libro', '=', fecha_anterior), ('planta', '=', libro.planta.id)], limit=1)

                if registro_anterior:
                    libro.saldo_inicial = registro_anterior.saldo_final
                elif not libro.saldo_inicial:
                    libro.saldo_inicial = 0.00  # Permitir introducir manualmente si no se encuentra registro anterior

                # --------------------------------------------------------- Fecha ---------------------------------------------------------
                fecha_entrada = init_date.strftime("%Y-%m-%d")
                fecha_salida = end_date.strftime("%Y-%m-%d")

                date_start = fecha_entrada + ' 00:00:00'
                date_end = fecha_salida + ' 23:59:59'

                date_start_search = datetime.strptime(date_start, '%Y-%m-%d %H:%M:%S') + timedelta(hours=abs(time_zone))
                date_end_search = datetime.strptime(date_end, '%Y-%m-%d %H:%M:%S') + timedelta(hours=abs(time_zone))

                linea = {}
                self.linea_libro_ids = [(5, 0, 0)]
                saldoaux = libro.saldo_inicial

                bancario_linea = self.env['account.bank.statement.line'].sudo().search(
                    [("line_ids.company_id.name", "=", libro.planta.name), ("date", ">=", libro.fecha_libro), ("date", "<=", libro.fecha_final)])
                for conta in bancario_linea:
                    if conta.transaction_type == 'Abono' or conta.transaction_type == 'Cargo':
                        linea['fecha'] = conta.date
                        linea['ingreso'] = 'Contado'
                        linea['fecha_rda'] = conta.date
                        linea['banco'] = 'BBVA'
                        linea['no_cuenta'] = conta.line_ids.journal_id.name
                        linea['descripcion'] = conta.payment_ref
                        if conta.transaction_type == 'Cargo':
                            linea['debe'] = (conta.amount) * (-1)
                            linea['haber'] = 0.00
                            saldoaux = saldoaux + (conta.amount) * (-1)
                        if conta.transaction_type == 'Abono':
                            linea['debe'] = 0.00
                            linea['haber'] = conta.amount
                            saldoaux = saldoaux - conta.amount
                        linea['saldo'] = saldoaux
                        self.linea_libro_ids = [(0, 0, linea)]

                dep = self.env['rpt_linea_corte_efectivo'].sudo().search(
                    [('linea_corte_efectivo.diario_x_dia', '>=', init_date), ('linea_corte_efectivo.diario_x_dia', '<=', end_date), ('linea_corte_efectivo.company_id.name', '=', libro.planta.name)])
                for deposito in dep:
                    linea['fecha'] = deposito.fecha.date()
                    linea['ingreso'] = 'Contado'
                    linea['fecha_rda'] = deposito.fecha.date()
                    linea['banco'] = 'BBVA'
                    linea['no_cuenta'] = deposito.cuenta
                    linea['descripcion'] = deposito.medio
                    linea['debe'] = deposito.monto
                    linea['haber'] = 0.00
                    saldoaux = saldoaux + deposito.monto
                    linea['saldo'] = saldoaux
                    self.linea_libro_ids = [(0, 0, linea)]
                #----------------------------CONSULTAS POR PAGOS EN PUNTO DE VENTA ---------------------------------------
                if not libro.responsable:
                    transferencias = self.env['pos.payment'].search(
                        [('payment_date', '>=', date_start_search), ('payment_date', '<=', date_end_search),
                         ('payment_method_id', '=', 'Transferencia'), ("x_studio_cancelado", "!=", True),
                         ("company_id.name", "=", libro.planta.name)])
                    vales = self.env['pos.payment'].search(
                        [('payment_date', '>=', date_start_search), ('payment_date', '<=', date_end_search),
                         ('payment_method_id', '=', 'Vale Gas'), ("x_studio_cancelado", "!=", True),
                         ("company_id.name", "=", libro.planta.name)])
                    cheques = self.env['pos.payment'].search(
                        [('payment_date', '>=', date_start_search), ('payment_date', '<=', date_end_search),
                         ('payment_method_id', '=', 'Cheque'), ("x_studio_cancelado", "!=", True),
                         ("company_id.name", "=", libro.planta.name)])
                else:
                    transferencias = self.env['pos.payment'].search(
                        [('payment_date', '>=', date_start_search), ('payment_date', '<=', date_end_search),
                         ('payment_method_id', '=', 'Transferencia'), ("x_studio_cancelado", "!=", True),
                         ('x_studio_responsable.name', '=', libro.responsable.name),
                         ("company_id.name", "=", libro.planta.name)])
                    vales = self.env['pos.payment'].search(
                        [('payment_date', '>=', date_start_search), ('payment_date', '<=', date_end_search),
                         ('payment_method_id', '=', 'Vale Gas'), ("x_studio_cancelado", "!=", True),
                         ('x_studio_responsable.name', '=', libro.responsable.name),
                         ("company_id.name", "=", libro.planta.name)])
                    cheques = self.env['pos.payment'].search(
                        [('payment_date', '>=', date_start_search), ('payment_date', '<=', date_end_search),
                         ('payment_method_id', '=', 'Cheque'), ("x_studio_cancelado", "!=", True),
                         ('x_studio_responsable.name', '=', libro.responsable.name),
                         ("company_id.name", "=", libro.planta.name)])
                #-----------------------------CONSULTAS POR INGRESOS -----------------------------------------------------    
                trans = self.env['rpt_linea_transferencia'].sudo().search(
                    [('linea_transferencia.diario_x_dia', '>=', init_date), ('linea_transferencia.diario_x_dia', '<=', end_date), ('linea_transferencia.company_id.name', '=', libro.planta.name)])
                vals = self.env['rpt_linea_vale_gas'].sudo().search(
                    [('linea_vale_gas.diario_x_dia', '>=', init_date), ('linea_vale_gas.diario_x_dia', '<=', end_date), ('linea_vale_gas.company_id.name', '=', libro.planta.name)])
                cheq = self.env['rpt_linea_cheque'].sudo().search(
                    [('linea_cheque.diario_x_dia', '>=', init_date), ('linea_cheque.diario_x_dia', '<=', end_date), ('linea_cheque.company_id.name', '=', libro.planta.name)])
                
                for transfer in trans:
                    linea['fecha'] = transfer.fecha_transferencia.date()
                    linea['ingreso'] = 'Contado'
                    linea['fecha_rda'] = transfer.fecha_transferencia.date()
                    linea['banco'] = 'BBVA'
                    linea['no_cuenta'] = transfer.cuenta.name  # dato temporal
                    linea['descripcion'] = transfer.payment_method_id
                    linea['debe'] = transfer.importe
                    linea['haber'] = 0.00
                    saldoaux = saldoaux + transfer.importe
                    linea['saldo'] = saldoaux
                    self.linea_libro_ids = [(0, 0, linea)]

                for valeg in vals:
                    linea['fecha'] = valeg.fecha_vale_gas.date()
                    linea['ingreso'] = 'Contado'
                    linea['fecha_rda'] = valeg.fecha_vale_gas.date()
                    linea['banco'] = 'BBVA'
                    linea['no_cuenta'] = valeg.cuenta.name  # dato temporal
                    linea['descripcion'] = valeg.payment_method_id
                    linea['debe'] = valeg.importe
                    linea['haber'] = 0.00
                    saldoaux = saldoaux + valeg.importe
                    linea['saldo'] = saldoaux
                    self.linea_libro_ids = [(0, 0, linea)]

                for cheqe in cheq:
                    linea['fecha'] = cheqe.fecha_cheque.date()
                    linea['ingreso'] = 'Contado'
                    linea['fecha_rda'] = cheqe.fecha_cheque.date()
                    linea['banco'] = 'BBVA'
                    linea['no_cuenta'] = cheqe.cuenta.name  # dato temporal
                    linea['descripcion'] = cheqe.payment_method_id
                    linea['debe'] = cheqe.importe
                    linea['haber'] = 0.00
                    saldoaux = saldoaux + cheqe.importe
                    linea['saldo'] = saldoaux
                    self.linea_libro_ids = [(0, 0, linea)]


class linea_libros(models.Model):  # segunda clase -----------------------------------------------------------------
    _name = 'libro_ingresos.linea_libro'
    _description = 'Linea de libro de ingresos'

    # llaves
    libro_id = fields.Many2one(comodel_name='libro_ingresos.libro', string='Libro de ingresos', readonly=True)  # relacion de tablas

    fecha = fields.Date(string='Fecha')
    ingreso = fields.Char(string='Ingreso')
    fecha_rda = fields.Date(string='Fecha RDA')
    banco = fields.Char(string='Banco')
    no_cuenta = fields.Char(string='No. Cuenta')
    descripcion = fields.Char(string='Descripción')
    debe = fields.Float(string='Debe', default=0.00)
    haber = fields.Float(string='Haber', default=0.00)
    saldo = fields.Float(string='Saldo', default=0.00)
