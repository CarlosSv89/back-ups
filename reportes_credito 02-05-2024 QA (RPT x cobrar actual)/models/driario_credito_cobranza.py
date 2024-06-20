from odoo import api, fields, models
import datetime


class DiarioCreditoCobranza(models.Model):
    _name = 'rep.diario.cyc'
    _description = 'Sábana diara acumulada'

    name = fields.Char(string='Nombre', default='Nuevo')
    fecha_inicio = fields.Date(string='Fecha inicial')
    fecha_final = fields.Date(string='Fecha final')
    linea_diario_ids = fields.One2many(comodel_name='rep.diario.cyc.line', inverse_name='diario_id', string='Líneas de sábana diara acumulada')
    company_id = fields.Many2one(comodel_name='res.company', required=True, default=lambda self: self.env.company)

    @api.model
    def create(self, vals):
        vals['name'] = 'Diario de crédito y cobranza: ' + vals['fecha_inicio'] + ' - ' + vals['fecha_final']
        return super(DiarioCreditoCobranza, self).create(vals)

    @api.onchange('fecha_inicio', 'fecha_final')
    def _calcular_valores(self):
        for i in self:
            if i.fecha_inicio and i.fecha_final:
                # 
                # credito_otorgado = self.env['credit.history'].search([('date', '<=', i.fecha_final), ('date', '>=', i.fecha_inicial)])
                # cobranzas = self.env['account.payment'].search([('date', '<=', i.fecha_final), ('date', '>=', i.fecha_inicial)])
                i.linea_diario_ids = [(5, 0, 0)]
                init_date = i.fecha_inicio
                it = 0
                while init_date <= i.fecha_final:
                    linea = {}
                    linea['date'] = init_date
                    if it > 0:
                        linea['saldo_inicial'] = i.linea_diario_ids[it - 1].saldo_final
                    else: 
                        fecha_busqueda = init_date + datetime.timedelta(days=-1)
                        ultima_linea = self.env['rep.diario.cyc.line'].search([('date', '=', fecha_busqueda), ('company_id', '=', self.env.company.id)], limit=1)
                        linea['saldo_inicial'] = ultima_linea.saldo_final
                    credito = 0.0
                    # Acumular el total de crédito otorgado en ese día
                    clientes = self.env['res.partner'].search([('x_studio_categoria_cliente', '=', 'Crédito')])
                    ordenes = self.env['pos.order'].search([('date_order', '>=', init_date.strftime("%Y-%m-%d") + " 07:00:00"), 
                    ('date_order', '<', (init_date + datetime.timedelta(days=1)).strftime("%Y-%m-%d") + " 06:59:59"), ('tipo_pago', '=', 'Crédito'), 
                    ("product_name", "not ilike", "Ajustes por cubicación"), ("product_name", "not ilike", "Compensación"),
                    ("product_name", "not ilike", "Ajuates por cubicación"),("product_name", "not ilike", "Auto consumo"),
                    ("product_name", "not ilike", "Traspasos"),("x_studio_cancelado","!=",True),
                    ('partner_id', 'in', clientes.ids)])
                    # credito_otorgado = self.env['credit.history'].search([('date', '=', init_date)])
                    # nota.amount_residual_signed for nota in notas
                    credito = sum(orden.amount_total for orden in ordenes) 
                    # for co in credito_otorgado:
                    #     credito += co.used_credit_amount
                    linea['credito_otorgado'] = credito
                    cobranzas = self.env['account.payment'].search([('date', '=', init_date), ('x_studio_tipo_de_pago', '=', 'Cobranza'), ('partner_id', 'in', clientes.ids), ('state', '=', 'posted')])
                    descuentos = self.env['account.move'].search([('invoice_date', '=', init_date), ('partner_id', 'in', clientes.ids),
                    ('state', '=', 'posted'), ('move_type', '=', 'out_refund'), ('edi_state','=','sent'), ('payment_state', '=', 'paid')])
                    linea['descuentos'] = sum(descuento.amount_total for descuento in descuentos)
                    cobranza = 0.0
                    for co in cobranzas:
                        cobranza += co.amount
                    linea['cobranza'] = cobranza
                    # print('' + linea['saldo_inicial'] + '' + linea['credito_otorgado'] + '' + linea['descuentos'] + '' + linea['cobranza'])
                    linea['subtotal'] = linea['saldo_inicial'] + linea['credito_otorgado'] - linea['descuentos'] - linea['cobranza']
                    linea['nota_cargo'] = 0.0
                    linea['cobranza_nota_cargo'] = 0.0
                    linea['cobranza_anticipada'] = 0.0
                    linea['ajuste_fuera_periodo'] = 0.0
                    linea['saldo_final'] = linea['subtotal'] + linea['nota_cargo'] + linea['cobranza_nota_cargo'] + linea['ajuste_fuera_periodo']
                    i.linea_diario_ids = [(0, 0, linea)]
                    it += 1
                    init_date = init_date + datetime.timedelta(days=1)


class LineaDiarioCreditoCobranza(models.Model):
    _name = 'rep.diario.cyc.line'
    _description = 'Linea de sábana diara acumulada'

    diario_id = fields.Many2one(comodel_name='rep.diario.cyc', string='Sábana diara acumulada', ondelete='cascade')
    date = fields.Date(string='Fecha')
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
    company_id = fields.Many2one(comodel_name='res.company', required=True, default=lambda self: self.env.company)


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    x_studio_tipo_de_pago = fields.Selection(string='Tipo de pago', selection=[('Cobranza', 'Cobranza'), ('Contado', 'Contado'), ('Pago anticipado', 'Pago anticipado')])
    

