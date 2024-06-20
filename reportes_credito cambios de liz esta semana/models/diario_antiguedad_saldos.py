from datetime import datetime, timedelta
import json
from odoo import api, fields, models


class AntiguedadSaldos(models.Model):
    _name = 'rep.diario.antiguedad.saldos'
    _description = 'Diario de antigüedad de saldos'

    name = fields.Char(string='Name', default='Nuevo')
    fecha = fields.Date(string='Fecha')
    categoria_rep = fields.Selection([
        ('general', 'General'),
        ('credito', 'Crédito'),
        ('servicio medido', 'Servicio medido')
    ], string='Categoría', default='general')
    linea_diario_ids = fields.One2many(comodel_name='rep.diario.antiguedad.saldos.linea', inverse_name='diario_id', string='Líneas de diario de antigüedad de saldos')
    company_id = fields.Many2one(comodel_name='res.company', required=True, default=lambda self: self.env.company)

    @api.model
    def create(self, vals):
        vals['name'] = 'Diario de antigüedad de saldos: ' + vals['fecha']
        return super(AntiguedadSaldos, self).create(vals)

    @api.onchange('fecha', 'categoria_rep')
    def _calcular_valores(self):
        for diario in self:
            if diario.fecha and diario.categoria_rep:
                diario.linea_diario_ids = [(5, 0, 0)]
                categoria = self.env['res.partner.category'].search([('name', '=', 'Crédito')])
                if diario.categoria_rep == "general":
                    clientes = self.env['res.partner'].search([('category_id', '=', categoria.id)])
                if diario.categoria_rep == "credito":
                    clientes = self.env['res.partner'].search([('category_id', '=', categoria.id),('servicio_medido', '=', False)])
                if diario.categoria_rep == "servicio medido":
                    clientes = self.env['res.partner'].search([('category_id', '=', categoria.id),('servicio_medido', '=', True)])
                for cliente in clientes:
                    # Dias de crédito
                    dias_credito_termino = self.env['account.payment.term'].search([('id', '=', cliente.property_payment_term_id.id)])
                    dias_de_credito = [0]
                    if dias_credito_termino:
                        dias_de_credito =  dias_credito_termino.name.split(' ', 1)
                    
                    # Notas de crédito
                    notas = all_notasC = self.env['account.move'].search([('partner_id', '=', cliente.id),('move_type', '=', 'out_refund'),('state', '!=',['cancel','draft']),('edi_state','=',['sent','to_cancel'])])
                    total = 0.0
                    total = sum(nota.amount_residual_signed for nota in notas)

                    # Pagos no aplicados
                    all_pagos = self.env['account.payment'].search([('partner_id', '=', cliente.id),('x_studio_tipo_de_pago', '=','Cobranza'),('state', '!=',['cancel','draft'])])
                    for all_p in all_pagos:
                        importe_p = 0.0
                        residual_p = 0.0
                        for p in  all_p.reconciled_invoice_ids.ids:
                            fac_p = self.env['account.move'].search([('id', '=', p)])
                            inf_w = json.loads(fac_p.invoice_payments_widget)
                            for pw in inf_w['content']:
                                if pw['journal_name'] != 'NDC':
                                    if pw['account_payment_id'] == all_p.payment_id.id:
                                        importe_p += pw['amount']
                        residual_p =  all_p.amount_total - importe_p

                        total += residual_p

                    linea = {'partner_id': cliente.id}
                    facturas_vencidas = self.env['account.move'].search([('invoice_date_due', '<=', diario.fecha), ('partner_id', '=', cliente.id), ('state', '=', 'posted'), ('move_type', '=', 'out_invoice'), ('payment_state', 'in', ['not_paid', 'partial', 'in_payment']), ('edi_state','=',['sent','to_cancel'])])
                    facturas_sin_vencer = self.env['account.move'].search([('invoice_date_due', '>', diario.fecha), ('partner_id', '=', cliente.id), ('state', '=', 'posted'), ('move_type', '=', 'out_invoice'), ('payment_state', 'in', ['not_paid', 'partial', 'in_payment']), ('edi_state','=',['sent','to_cancel'])])
                    ordenes = self.env['pos.order'].search([('partner_id', '=', cliente.id), ('state', '=', 'done'), ('tipo_pago', '!=', 'Efectivo')])
                    sin_vencer = 0.0
                    vencido = 0.0
                    vencido1 = 0.0
                    vencido2 = 0.0
                    vencido3 = 0.0
                    vencido4 = 0.0
                    vencido5 = 0.0
                    vencido = sum(factura.amount_residual_signed for factura in facturas_vencidas)
                    sin_vencer = sum(factura.amount_residual_signed for factura in facturas_sin_vencer)
                    for factura in facturas_vencidas:
                        fecha_venc = factura.invoice_date_due
                        # if fecha_venc <= hoy:
                        #     vencido += factura.amount_residual_signed
                        dias_vencido = (diario.fecha - fecha_venc)
                        if dias_vencido.days < 16:
                            vencido1 += factura.amount_residual_signed
                        elif dias_vencido.days < 31:
                            vencido2 += factura.amount_residual_signed
                        elif dias_vencido.days < 61:
                            vencido3 += factura.amount_residual_signed
                        elif dias_vencido.days < 91:
                            vencido4 += factura.amount_residual_signed
                        else:
                            vencido5 += factura.amount_residual_signed

                    for orden in ordenes:
                        order_vencida_due = orden.date_order + timedelta(days=int(dias_de_credito[0]))
                        if order_vencida_due.date() <= diario.fecha:
                            vencido += orden.amount_total
                            dias_vencido = (diario.fecha - order_vencida_due.date())
                            if dias_vencido.days < 16:
                                vencido1 += orden.amount_total
                            elif dias_vencido.days < 31:
                                vencido2 += orden.amount_total
                            elif dias_vencido.days < 61:
                                vencido3 += orden.amount_total
                            elif dias_vencido.days < 91:
                                vencido4 += orden.amount_total
                            else:
                                vencido5 += orden.amount_total
                        else:
                            sin_vencer += orden.amount_total
                    linea['al_corriente'] = sin_vencer
                    linea['vencido'] = vencido
                    linea['subtotal'] = linea['al_corriente'] + linea['vencido']
                    linea['vencido_1_15'] = vencido1
                    linea['vencido_16_30'] = vencido2
                    linea['vencido_31_60'] = vencido3
                    linea['vencido_61_90'] = vencido4
                    linea['vencido_91_mas'] = vencido5
                    linea['saldo_favor'] = total
                    linea['saldo_total'] = linea['subtotal'] - total
                    diario.linea_diario_ids = [(0, 0, linea)]
    

class AntiguedadSaldosLinea(models.Model):
    _name = 'rep.diario.antiguedad.saldos.linea'
    _description = 'Linea de antigüedad de saldos'

    diario_id = fields.Many2one(string='Diario de antigüedad de saldos', comodel_name='rep.diario.antiguedad.saldos', ondelete='cascade')
    partner_id = fields.Many2one(comodel_name='res.partner', string='Cliente')
    dias_credito = fields.Many2one(comodel_name='account.payment.term', related='partner_id.property_payment_term_id')
    subtotal = fields.Float(string='Subtotal', digits=(14,2))
    al_corriente = fields.Float(string='Al corriente', digits=(14,2))
    vencido = fields.Float(string='Vencido', digits=(14,2))
    vencido_1_15 = fields.Float(string='1-15 días')
    vencido_16_30 = fields.Float(string='15-30 días')
    vencido_31_60 = fields.Float(string='31-60 días')
    vencido_61_90 = fields.Float(string='61-90 días')
    vencido_91_mas = fields.Float(string='91-mas días')
    saldo_favor = fields.Float(string='Saldo a favor', digits=(14,2))
    saldo_total = fields.Float(string='Saldo total', digits=(14,2))
    clasificacion = fields.Char(string='Clasificación', digits=(14,2))