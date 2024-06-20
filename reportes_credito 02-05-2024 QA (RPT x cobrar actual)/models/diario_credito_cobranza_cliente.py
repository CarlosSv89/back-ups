from odoo import api, fields, models
import datetime


class DiarioClienteCreditoCobranza(models.Model):
    _name = 'rep.diario.cliente.cyc'
    _description = 'Sábana detallada por cliente'

    name = fields.Char(string='Nombre', default='Nuevo')
    fecha_inicio = fields.Date(string='Fecha inicial')
    fecha_final = fields.Date(string='Fecha final')
    linea_diario_ids = fields.One2many(comodel_name='rep.diario.cliente.cyc.line', inverse_name='diario_id', string='Líneas de diario de crédito y cobranza por cliente')
    company_id = fields.Many2one(comodel_name='res.company', required=True, default=lambda self: self.env.company)

    @api.model
    def create(self, vals):
        vals['name'] = 'Sábana detallada por cliente: ' + vals['fecha_inicio'] + ' - ' + vals['fecha_final']
        return super(DiarioClienteCreditoCobranza, self).create(vals)

    @api.onchange('fecha_inicio', 'fecha_final')
    def _calcular_valores(self):
        for i in self:
            if i.fecha_inicio and i.fecha_final:
                i.linea_diario_ids = [(5, 0, 0)]
                clientes = self.env['res.partner'].search([('x_studio_categoria_cliente', '=', 'Crédito')])
                for cliente in clientes:
                    linea = {}
                    linea['fecha'] = i.fecha_final
                    linea['partner_id'] = cliente.id
                    fecha_busqueda = i.fecha_inicio + datetime.timedelta(days=-1)
                    ultima_linea = self.env['rep.diario.cliente.cyc.line'].search([('fecha', '=', fecha_busqueda), ('partner_id', '=', cliente.id)])
                    if ultima_linea:
                        linea['saldo_inicial'] = ultima_linea.saldo_final
                    else:
                        linea['saldo_inicial'] = 0.0
                    credito = 0.0
                    # Acumular el total de crédito otorgado entre fechas
                    ordenes = self.env['pos.order'].search([('partner_id', '=', cliente.id), ('date_order', '>=', i.fecha_inicio.strftime("%Y-%m-%d") + " 07:00:00"), 
                    ('date_order', '<', (i.fecha_final + datetime.timedelta(days=1)).strftime("%Y-%m-%d") + " 06:59:59"), ('tipo_pago', '=', 'Crédito'), 
                    ("product_name", "not ilike", "Ajustes por cubicación"), ("product_name", "not ilike", "Compensación"),
                    ("product_name", "not ilike", "Ajuates por cubicación"),("product_name", "not ilike", "Auto consumo"),
                    ("product_name", "not ilike", "Traspasos"),("x_studio_cancelado","!=",True)])
                    credito = sum(orden.amount_total for orden in ordenes) 
                    # credito_otorgado = self.env['credit.history'].search([('date', '>=', i.fecha_inicio), ('date', '<=', i.fecha_final), ('partner_id', '=', cliente.id)])
                    # for co in credito_otorgado:
                    #     credito += co.used_credit_amount
                    linea['credito_otorgado'] = credito
                    cobranzas = self.env['account.payment'].search([('date', '>=', i.fecha_inicio), ('date', '<=', i.fecha_final), ('x_studio_tipo_de_pago', '=', 'Cobranza'), ('partner_id', '=', cliente.id), ('state', '=', 'posted')])
                    descuentos = self.env['account.move'].search([('invoice_date', '>=', i.fecha_inicio), ('invoice_date', '<', i.fecha_final), 
                    ('partner_id', '=', cliente.id), ('state', '=', 'posted'), ('move_type', '=', 'out_refund'), ('edi_state','=','sent'), ('payment_state', '=', 'paid')])
                    linea['descuentos'] = sum(descuento.amount_total for descuento in descuentos)
                    cobranza = 0.0
                    for co in cobranzas:
                        cobranza += co.amount
                    linea['cobranza'] = cobranza
                    linea['subtotal'] = linea['saldo_inicial'] + linea['credito_otorgado'] - linea['descuentos'] - linea['cobranza']
                    linea['nota_cargo'] = 0.0
                    linea['cobranza_nota_cargo'] = 0.0
                    linea['cobranza_anticipada'] = 0.0
                    linea['ajuste_fuera_periodo'] = 0.0
                    linea['saldo_final'] = linea['subtotal'] + linea['nota_cargo'] + linea['cobranza_nota_cargo'] + linea['ajuste_fuera_periodo']
                    i.linea_diario_ids = [(0, 0, linea)]


class LineaDiarioClienteCreditoCobranza(models.Model):
    _name = 'rep.diario.cliente.cyc.line'
    _description = 'Linea de sábana detallada por cliente'

    diario_id = fields.Many2one(comodel_name='rep.diario.cliente.cyc', string='Sábana detallada por cliente', ondelete='cascade')
    fecha = fields.Date(string="Fecha")
    partner_id = fields.Many2one(comodel_name='res.partner', string='Cliente')
    saldo_inicial = fields.Float(string='Saldo inicial', digits=(19,2))
    credito_otorgado = fields.Float(string='Crédito otorgado', digits=(19,2))
    descuentos = fields.Float(string='Descuentos', digits=(19,2))
    cobranza = fields.Float(string='Cobranza', digits=(19,2))
    subtotal = fields.Float(string='Subtotal', digits=(19,2))
    nota_cargo = fields.Float(string='Nota de cargo', digits=(19,2))
    cobranza_nota_cargo = fields.Float(string='Cobranza de nota de cargo', digits=(19,2) )
    cobranza_anticipada = fields.Float(string='Cobranza anticipada', digits=(19,2))
    ajuste_fuera_periodo = fields.Float(string='Ajustes fuera del periodo', digits=(19,2))
    saldo_final = fields.Float(string='Saldo final', digits=(19,2))
