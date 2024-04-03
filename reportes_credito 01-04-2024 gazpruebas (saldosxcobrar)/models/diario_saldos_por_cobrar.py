import datetime
import calendar
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
import json
import locale
import logging

_logger = logging.getLogger(__name__)

class SaldoPorCobrar(models.Model):
    _name = 'rep.diario.saldos.xcobrar'
    _description = 'Diario de saldos por cobrar mensual'

    name = fields.Char(string='Nombre', default='Nuevo')
    company_name = fields.Char(string='Compañia')
    company_id = fields.Many2one(comodel_name='res.company', required=True, default=lambda self: self.env.company)
    fecha_report = fields.Date(string='Fecha del reporte')
    fecha_inicial = fields.Date(string='Fecha inicial')
    fecha_final = fields.Date(string='Fecha final')
    linea_diario_rpt = fields.One2many(comodel_name='saldos.xcobrar.linea', inverse_name='diario_id', string='Lineas de saldos por cobrar')
    linea_desglose_ordenes = fields.Many2many(comodel_name='desglose.ordenes.linea',  string='Lineas de desglose de ordenes')
    linea_desglose_facturas = fields.Many2many(comodel_name='desglose.facturas.linea', string='Lineas de desglose de facturas')

    can_edit_report = fields.Boolean(string='Can edit report?', default=False )

    @api.model
    def create(self, vals):
        vals['name'] =  'Saldos por cobrar del ' + vals['fecha_inicial'] + ' al ' + vals['fecha_final']
        return super(SaldoPorCobrar, self).create(vals)


    @api.onchange('fecha_inicial', 'fecha_final')
    def _calcular_valores(self):
        for i in self:
            if i.fecha_final and i.fecha_inicial:

                self.can_edit_report = True
                self.company_name = self.env.company.name
                locale.setlocale(locale.LC_ALL, ("es_ES", "UTF-8"))
                i.fecha_report = datetime.datetime.now().date()

                i.linea_diario_rpt = [(5, 0, 0)]
                i.linea_desglose_ordenes = [(5, 0, 0)]
                i.linea_desglose_facturas = [(5, 0, 0)]
                mes = 1

                facturas = self.env['account.move'].search([('invoice_date_due', '>=', i.fecha_inicial),('invoice_date_due', '<=', i.fecha_final),('move_type', '=', 'out_invoice'),('state', '=', 'posted'),('edi_state','in',['sent','to_cancel']),('x_studio_tipo', '=', 'Crédito')])
                ordenes = self.env['pos.order'].search([('state', '=','done'),('x_studio_cancelado','=',False),('tipo_pago','=','Crédito'),('amount_total','!=',0.00),('x_studio_dias_credito','!=',False)])
                
                # Cobranza meta
                i.linea_diario_rpt = [(0, 0, self._crear_linea_meta('Cobranza meta', facturas, ordenes, i.fecha_inicial, i.fecha_final))] 
                
                # Descuentos
                i.linea_diario_rpt = [(0, 0, self._crear_linea_descuentos('Descuentos del perdiodo', facturas, i.fecha_inicial, i.fecha_final))]

                # Pagos de meses anteriores
                i.linea_diario_rpt = [(0, 0, self._crear_linea_pagos_meses_anteriores('Cobranza meses anteriores', facturas, i.fecha_inicial, i.fecha_final))]


                while mes <= 12:
                    if mes == 1:
                        i.linea_diario_rpt = [(0, 0, self._crear_linea_mes('Enero', facturas, mes, i.fecha_inicial, i.fecha_final))]
                    if mes == 2:
                        i.linea_diario_rpt = [(0, 0, self._crear_linea_mes('Febrero', facturas, mes, i.fecha_inicial, i.fecha_final))]
                    if mes == 3:
                        i.linea_diario_rpt = [(0, 0, self._crear_linea_mes('Marzo', facturas, mes, i.fecha_inicial, i.fecha_final))]
                    if mes == 4:
                        i.linea_diario_rpt = [(0, 0, self._crear_linea_mes('Abril', facturas, mes, i.fecha_inicial, i.fecha_final))]
                    if mes == 5:
                        i.linea_diario_rpt = [(0, 0, self._crear_linea_mes('Mayo', facturas, mes, i.fecha_inicial, i.fecha_final))]
                    if mes == 6:
                        i.linea_diario_rpt = [(0, 0, self._crear_linea_mes('Junio', facturas, mes, i.fecha_inicial, i.fecha_final))]
                    if mes == 7:
                        i.linea_diario_rpt = [(0, 0, self._crear_linea_mes('Julio', facturas, mes, i.fecha_inicial, i.fecha_final))]
                    if mes == 8:
                        i.linea_diario_rpt = [(0, 0, self._crear_linea_mes('Agosto', facturas, mes, i.fecha_inicial, i.fecha_final))]
                    if mes == 9:
                        i.linea_diario_rpt = [(0, 0, self._crear_linea_mes('Septiembre', facturas, mes, i.fecha_inicial, i.fecha_final))]
                    if mes == 10:
                        i.linea_diario_rpt = [(0, 0, self._crear_linea_mes('Octubre', facturas, mes, i.fecha_inicial, i.fecha_final))]
                    if mes == 11:
                        i.linea_diario_rpt = [(0, 0, self._crear_linea_mes('Noviembre', facturas, mes, i.fecha_inicial, i.fecha_final))]
                    if mes == 12:
                        i.linea_diario_rpt = [(0, 0, self._crear_linea_mes('Diciembre', facturas, mes, i.fecha_inicial, i.fecha_final))]
                    mes += 1
                    
                self.can_edit_report = False

    def _crear_linea_pagos_meses_anteriores(self, concepto, facturas, fecha_inicio, fecha_fin):
        linea = {}
        linea['concepto'] = concepto
        vals = {
            "enero_2022": 0.0,
            "febrero_2022": 0.0,
            "marzo_2022": 0.0,
            "abril_2022": 0.0,
            "mayo_2022": 0.0,
            "junio_2022": 0.0,
            "julio_2022": 0.0,
            "agosto_2022": 0.0,
            "septiembre_2022": 0.0,
            "octubre_2022": 0.0,
            "noviembre_2022": 0.0,
            "diciembre_2022": 0.0,
            
            "enero_2023": 0.0,
            "febrero_2023": 0.0,
            "marzo_2023": 0.0,
            "abril_2023": 0.0,
            "mayo_2023": 0.0,
            "junio_2023": 0.0,
            "julio_2023": 0.0,
            "agosto_2023": 0.0,
            "septiembre_2023": 0.0,
            "octubre_2023": 0.0,
            "noviembre_2023": 0.0,
            "diciembre_2023": 0.0,
            
            "enero_2024": 0.0,
            "febrero_2024": 0.0,
            "marzo_2024": 0.0,
            "abril_2024": 0.0,
            "mayo_2024": 0.0,
            "junio_2024": 0.0,
            "julio_2024": 0.0,
            "agosto_2024": 0.0,
            "septiembre_2024": 0.0,
            "octubre_2024": 0.0,
            "noviembre_2024": 0.0,
            "diciembre_2024": 0.0,
        }
        

        # variable para menejar validacion por mes y año
        date_alt = fecha_inicio
        
        while date_alt <= fecha_fin:
            fecha_final = fecha_inicio + relativedelta(months=1)
            fac_mes = facturas.filtered(lambda fac_mes: fac_mes.invoice_date_due >= fecha_inicio and fac_mes.invoice_date_due < fecha_final)
            for factura in fac_mes:
                pagos = json.loads(factura.invoice_payments_widget)
                if pagos:
                    for pago in pagos['content']:
                        if pago['journal_name'] != 'NDC':
                            datetimeobj=datetime.datetime.strptime(pago['date'],"%Y-%m-%d")
                            if datetimeobj.date() < fecha_inicio:
                                if date_alt.month  == 1:
                                    vals[f"enero_{date_alt.year}"]+= pago['amount']
                                elif date_alt.month == 2:
                                    vals[f"febrero_{date_alt.year}"]+= pago['amount']
                                elif date_alt.month == 3:
                                    vals[f"marzo_{date_alt.year}"]+= pago['amount']
                                elif date_alt.month == 4:
                                    vals[f"abril_{date_alt.year}"]+= pago['amount']
                                elif date_alt.month == 5:
                                    vals[f"mayo_{date_alt.year}"]+= pago['amount']
                                elif date_alt.month == 6:
                                    vals[f"junio_{date_alt.year}"]+= pago['amount']
                                elif date_alt.month == 7:
                                    vals[f"julio_{date_alt.year}"]+= pago['amount']
                                elif date_alt.month == 8:
                                    vals[f"agosto_{date_alt.year}"]+= pago['amount']
                                elif date_alt.month == 9:
                                    vals[f"septiembre_{date_alt.year}"]+= pago['amount']
                                elif date_alt.month == 10:
                                    vals[f"octubre_{date_alt.year}"]+= pago['amount']
                                elif date_alt.month == 11:
                                    vals[f"noviembre_{date_alt.year}"]+= pago['amount']
                                elif date_alt.month == 12:
                                    vals[f"diciembre_{date_alt.year}"]+= pago['amount']
            fecha_inicio = fecha_final
            # mes += 1
            date_alt = date_alt + relativedelta(months=1)
        
        linea['enero_2022'] = -1 * vals['enero_2022']
        linea['febrero_2022'] = -1 * vals['febrero_2022']
        linea['marzo_2022'] = -1 * vals['marzo_2022']
        linea['abril_2022'] = -1 * vals['abril_2022']
        linea['mayo_2022'] = -1 * vals['mayo_2022']
        linea['junio_2022'] = -1 * vals['junio_2022']
        linea['julio_2022'] = -1 * vals['julio_2022']
        linea['agosto_2022'] = -1 * vals['agosto_2022']
        linea['septiembre_2022'] = -1 * vals['septiembre_2022']
        linea['octubre_2022'] = -1 * vals['octubre_2022']
        linea['noviembre_2022'] = -1 * vals['noviembre_2022']
        linea['diciembre_2022'] = -1 * vals['diciembre_2022']
        linea['enero_2023'] = -1 * vals['enero_2023']
        linea['febrero_2023'] = -1 * vals['febrero_2023']
        linea['marzo_2023'] = -1 * vals['marzo_2023']
        linea['abril_2023'] = -1 * vals['abril_2023']
        linea['mayo_2023'] = -1 * vals['mayo_2023']
        linea['junio_2023'] = -1 * vals['junio_2023']
        linea['julio_2023'] = -1 * vals['julio_2023']
        linea['agosto_2023'] = -1 * vals['agosto_2023']
        linea['septiembre_2023'] = -1 * vals['septiembre_2023']
        linea['octubre_2023'] = -1 * vals['octubre_2023']
        linea['noviembre_2023'] = -1 * vals['noviembre_2023']
        linea['diciembre_2023'] = -1 * vals['diciembre_2023']
        linea['enero_2024'] = -1 * vals['enero_2024']
        linea['febrero_2024'] = -1 * vals['febrero_2024']
        linea['marzo_2024'] = -1 * vals['marzo_2024']
        linea['abril_2024'] = -1 * vals['abril_2024']
        linea['mayo_2024'] = -1 * vals['mayo_2024']
        linea['junio_2024'] = -1 * vals['junio_2024']
        linea['julio_2024'] = -1 * vals['julio_2024']
        linea['agosto_2024'] = -1 * vals['agosto_2024']
        linea['septiembre_2024'] = -1 * vals['septiembre_2024']
        linea['octubre_2024'] = -1 * vals['octubre_2024']
        linea['noviembre_2024'] = -1 * vals['noviembre_2024']
        linea['diciembre_2024'] = -1 * vals['diciembre_2024']
        return linea

    def _crear_linea_descuentos(self, concepto, facturas, fecha_inicio, fecha_fin):
        linea = {}
        linea['concepto'] = concepto
        vals = {
            "enero_2022": 0.0,
            "febrero_2022": 0.0,
            "marzo_2022": 0.0,
            "abril_2022": 0.0,
            "mayo_2022": 0.0,
            "junio_2022": 0.0,
            "julio_2022": 0.0,
            "agosto_2022": 0.0,
            "septiembre_2022": 0.0,
            "octubre_2022": 0.0,
            "noviembre_2022": 0.0,
            "diciembre_2022": 0.0,
            
            "enero_2023": 0.0,
            "febrero_2023": 0.0,
            "marzo_2023": 0.0,
            "abril_2023": 0.0,
            "mayo_2023": 0.0,
            "junio_2023": 0.0,
            "julio_2023": 0.0,
            "agosto_2023": 0.0,
            "septiembre_2023": 0.0,
            "octubre_2023": 0.0,
            "noviembre_2023": 0.0,
            "diciembre_2023": 0.0,
            
            "enero_2024": 0.0,
            "febrero_2024": 0.0,
            "marzo_2024": 0.0,
            "abril_2024": 0.0,
            "mayo_2024": 0.0,
            "junio_2024": 0.0,
            "julio_2024": 0.0,
            "agosto_2024": 0.0,
            "septiembre_2024": 0.0,
            "octubre_2024": 0.0,
            "noviembre_2024": 0.0,
            "diciembre_2024": 0.0,
        }
        

        # variable para menejar validacion por mes y año
        date_alt = fecha_inicio

        while date_alt <= fecha_fin:
            fecha_final = fecha_inicio + relativedelta(months=1)
            fac_mes = facturas.filtered(lambda fac_mes: fac_mes.invoice_date_due >= fecha_inicio and fac_mes.invoice_date_due < fecha_final)
            if fac_mes:
                for factura in fac_mes:
                    descuentos = json.loads(factura.invoice_payments_widget)
                    if descuentos:
                        for nota in descuentos['content']:
                            if nota['journal_name'] == 'NDC':
                                # datetimeobj=datetime.datetime.strptime(nota['date'],"%Y-%m-%d")
                                # if  datetimeobj.month  == mes_search and  datetimeobj.date()  >= fecha_inicio:
                                if date_alt.month  == 1:
                                    vals[f"enero_{date_alt.year}"]+= nota['amount']
                                elif date_alt.month == 2:
                                    vals[f"febrero_{date_alt.year}"]+= nota['amount']
                                elif date_alt.month == 3:
                                    vals[f"marzo_{date_alt.year}"]+= nota['amount']
                                elif date_alt.month == 4:
                                    vals[f"abril_{date_alt.year}"]+= nota['amount']
                                elif date_alt.month == 5:
                                    vals[f"mayo_{date_alt.year}"]+= nota['amount']
                                elif date_alt.month == 6:
                                    vals[f"junio_{date_alt.year}"]+= nota['amount']
                                elif date_alt.month == 7:
                                    vals[f"julio_{date_alt.year}"]+= nota['amount']
                                elif date_alt.month == 8:
                                    vals[f"agosto_{date_alt.year}"]+= nota['amount']
                                elif date_alt.month == 9:
                                    vals[f"septiembre_{date_alt.year}"]+= nota['amount']
                                elif date_alt.month == 10:
                                    vals[f"octubre_{date_alt.year}"]+= nota['amount']
                                elif date_alt.month == 11:
                                    vals[f"noviembre_{date_alt.year}"]+= nota['amount']
                                elif date_alt.month == 12:
                                    vals[f"diciembre_{date_alt.year}"]+= nota['amount']                                                   

            fecha_inicio = fecha_final
            # mes += 1
            date_alt = date_alt + relativedelta(months=1)
         
        linea['enero_2022'] = -1 * vals['enero_2022']
        linea['febrero_2022'] = -1 * vals['febrero_2022']
        linea['marzo_2022'] = -1 * vals['marzo_2022']
        linea['abril_2022'] = -1 * vals['abril_2022']
        linea['mayo_2022'] = -1 * vals['mayo_2022']
        linea['junio_2022'] = -1 * vals['junio_2022']
        linea['julio_2022'] = -1 * vals['julio_2022']
        linea['agosto_2022'] = -1 * vals['agosto_2022']
        linea['septiembre_2022'] = -1 * vals['septiembre_2022']
        linea['octubre_2022'] = -1 * vals['octubre_2022']
        linea['noviembre_2022'] = -1 * vals['noviembre_2022']
        linea['diciembre_2022'] = -1 * vals['diciembre_2022']
        linea['enero_2023'] = -1 * vals['enero_2023']
        linea['febrero_2023'] = -1 * vals['febrero_2023']
        linea['marzo_2023'] = -1 * vals['marzo_2023']
        linea['abril_2023'] = -1 * vals['abril_2023']
        linea['mayo_2023'] = -1 * vals['mayo_2023']
        linea['junio_2023'] = -1 * vals['junio_2023']
        linea['julio_2023'] = -1 * vals['julio_2023']
        linea['agosto_2023'] = -1 * vals['agosto_2023']
        linea['septiembre_2023'] = -1 * vals['septiembre_2023']
        linea['octubre_2023'] = -1 * vals['octubre_2023']
        linea['noviembre_2023'] = -1 * vals['noviembre_2023']
        linea['diciembre_2023'] = -1 * vals['diciembre_2023']
        linea['enero_2024'] = -1 * vals['enero_2024']
        linea['febrero_2024'] = -1 * vals['febrero_2024']
        linea['marzo_2024'] = -1 * vals['marzo_2024']
        linea['abril_2024'] = -1 * vals['abril_2024']
        linea['mayo_2024'] = -1 * vals['mayo_2024']
        linea['junio_2024'] = -1 * vals['junio_2024']
        linea['julio_2024'] = -1 * vals['julio_2024']
        linea['agosto_2024'] = -1 * vals['agosto_2024']
        linea['septiembre_2024'] = -1 * vals['septiembre_2024']
        linea['octubre_2024'] = -1 * vals['octubre_2024']
        linea['noviembre_2024'] = -1 * vals['noviembre_2024']
        linea['diciembre_2024'] = -1 * vals['diciembre_2024']
        return linea


    def _crear_linea_meta(self, concepto, facturas, ordenes, fecha_inicio, fecha_fin):
        linea = {}
        linea['concepto'] = concepto
        vals = {
            "enero_2022": 0.0,
            "febrero_2022": 0.0,
            "marzo_2022": 0.0,
            "abril_2022": 0.0,
            "mayo_2022": 0.0,
            "junio_2022": 0.0,
            "julio_2022": 0.0,
            "agosto_2022": 0.0,
            "septiembre_2022": 0.0,
            "octubre_2022": 0.0,
            "noviembre_2022": 0.0,
            "diciembre_2022": 0.0,
            
            "enero_2023": 0.0,
            "febrero_2023": 0.0,
            "marzo_2023": 0.0,
            "abril_2023": 0.0,
            "mayo_2023": 0.0,
            "junio_2023": 0.0,
            "julio_2023": 0.0,
            "agosto_2023": 0.0,
            "septiembre_2023": 0.0,
            "octubre_2023": 0.0,
            "noviembre_2023": 0.0,
            "diciembre_2023": 0.0,
            
            "enero_2024": 0.0,
            "febrero_2024": 0.0,
            "marzo_2024": 0.0,
            "abril_2024": 0.0,
            "mayo_2024": 0.0,
            "junio_2024": 0.0,
            "julio_2024": 0.0,
            "agosto_2024": 0.0,
            "septiembre_2024": 0.0,
            "octubre_2024": 0.0,
            "noviembre_2024": 0.0,
            "diciembre_2024": 0.0,
        }
        
        
        linea_facturas = {}
        linea_ordenes = {}       

        # variable para menejar validacion por mes y año
        date_alt = fecha_inicio

        
        
        while date_alt <= fecha_fin:
            fecha_final = fecha_inicio + relativedelta(months=1)
            if fecha_inicio == fecha_fin:
                f = facturas.filtered(lambda f: f.invoice_date_due == fecha_inicio)
            else:
                f = facturas.filtered(lambda f: f.invoice_date_due >= fecha_inicio and f.invoice_date_due < fecha_final)

            for factura in f:
                if date_alt.month == 1:
                    vals[f"enero_{date_alt.year}"]+= factura.amount_total_signed
                if date_alt.month == 2:
                    vals[f"febrero_{date_alt.year}"]+= factura.amount_total_signed
                if date_alt.month == 3:
                    vals[f"marzo_{date_alt.year}"]+= factura.amount_total_signed
                if date_alt.month == 4:
                    vals[f"abril_{date_alt.year}"]+= factura.amount_total_signed
                if date_alt.month == 5:
                    vals[f"mayo_{date_alt.year}"]+= factura.amount_total_signed
                if date_alt.month == 6:
                    vals[f"junio_{date_alt.year}"]+= factura.amount_total_signed
                if date_alt.month == 7:
                    vals[f"julio_{date_alt.year}"]+= factura.amount_total_signed
                if date_alt.month == 8:
                    vals[f"agosto_{date_alt.year}"]+= factura.amount_total_signed
                if date_alt.month == 9:
                    vals[f"septiembre_{date_alt.year}"]+= factura.amount_total_signed
                if date_alt.month == 10:
                    vals[f"octubre_{date_alt.year}"]+= factura.amount_total_signed
                if date_alt.month == 11:
                    vals[f"noviembre_{date_alt.year}"]+= factura.amount_total_signed
                if date_alt.month == 12:
                    vals[f"diciembre_{date_alt.year}"]+= factura.amount_total_signed

                # Facturas residual(no pagadas)
                if factura.amount_residual_signed != 0.00:
                    linea_facturas['concepto'] = calendar.month_name[date_alt.month]
                    linea_facturas['name'] = factura.name
                    linea_facturas['l10n_mx_edi_cfdi_uuid'] = factura.l10n_mx_edi_cfdi_uuid
                    linea_facturas['invoice_partner_display_name'] = factura.invoice_partner_display_name
                    linea_facturas['invoice_date'] = factura.invoice_date
                    linea_facturas['invoice_date_due'] = factura.invoice_date_due
                    linea_facturas['amount_total'] = factura.amount_total
                    linea_facturas['amount_residual_signed'] = factura.amount_residual_signed
                    linea_facturas['edi_state'] = factura.edi_state
                    linea_facturas['payment_state'] = factura.payment_state
                    linea_facturas['state'] = factura.state
                        
                    self.linea_desglose_facturas = [(0,0,linea_facturas)]


                orden_valida = False
            for order_vencida in ordenes:
                dias_de_credito = {}
                dias_de_credito =  order_vencida.x_studio_dias_credito.split(' ', 1)
                order_vencida_due = order_vencida.date_order + datetime.timedelta(days=int(dias_de_credito[0])) 
                if order_vencida_due.date() <= fecha_fin:

                    if fecha_inicio == fecha_fin:
                        if (order_vencida_due.date() == fecha_inicio):
                            orden_valida = True
                        else:
                            orden_valida = False
                    else: 
                        if (order_vencida_due.date() >= fecha_inicio and order_vencida_due.date() < fecha_final):
                            orden_valida = True
                        else:
                            orden_valida = False

                    if(orden_valida):
                        if date_alt.month == 1:
                            vals[f"enero_{date_alt.year}"]+= order_vencida.amount_total
                        if date_alt.month == 2:
                            vals[f"febrero_{date_alt.year}"]+= order_vencida.amount_total
                        if date_alt.month == 3:
                            vals[f"marzo_{date_alt.year}"]+= order_vencida.amount_total
                        if date_alt.month == 4:
                            vals[f"abril_{date_alt.year}"]+= order_vencida.amount_total
                        if date_alt.month == 5:
                            vals[f"mayo_{date_alt.year}"]+= order_vencida.amount_total
                        if date_alt.month == 6:
                            vals[f"junio_{date_alt.year}"]+= order_vencida.amount_total
                        if date_alt.month == 7:
                            vals[f"julio_{date_alt.year}"]+= order_vencida.amount_total
                        if date_alt.month == 8:
                            vals[f"agosto_{date_alt.year}"]+= order_vencida.amount_total
                        if date_alt.month == 9:
                            vals[f"septiembre_{date_alt.year}"]+= order_vencida.amount_total
                        if date_alt.month == 10:
                            vals[f"octubre_{date_alt.year}"]+= order_vencida.amount_total
                        if date_alt.month == 11:
                            vals[f"noviembre_{date_alt.year}"]+= order_vencida.amount_total
                        if date_alt.month == 12:
                            vals[f"diciembre_{date_alt.year}"]+= order_vencida.amount_total

                        # Ordenes de credito(no se han facturado)
                        linea_ordenes['concepto'] = calendar.month_name[date_alt.month]
                        linea_ordenes['date_order'] = order_vencida.date_order.date()
                        linea_ordenes['date_order_due'] = order_vencida_due.date()
                        linea_ordenes['order_folio'] = order_vencida.order_folio
                        linea_ordenes['partner_id'] = order_vencida.partner_id
                        linea_ordenes['amount_total'] = order_vencida.amount_total

                        self.linea_desglose_ordenes = [(0,0,linea_ordenes)]

            fecha_inicio = fecha_final
            # mes += 1
            date_alt = date_alt + relativedelta(months=1)

        linea['enero_2022'] = vals['enero_2022']
        linea['febrero_2022'] = vals['febrero_2022']
        linea['marzo_2022'] = vals['marzo_2022']
        linea['abril_2022'] = vals['abril_2022']
        linea['mayo_2022'] = vals['mayo_2022']
        linea['junio_2022'] = vals['junio_2022']
        linea['julio_2022'] = vals['julio_2022']
        linea['agosto_2022'] = vals['agosto_2022']
        linea['septiembre_2022'] = vals['septiembre_2022']
        linea['octubre_2022'] = vals['octubre_2022']
        linea['noviembre_2022'] = vals['noviembre_2022']
        linea['diciembre_2022'] = vals['diciembre_2022']
        linea['enero_2023'] = vals['enero_2023']
        linea['febrero_2023'] = vals['febrero_2023']
        linea['marzo_2023'] = vals['marzo_2023']
        linea['abril_2023'] = vals['abril_2023']
        linea['mayo_2023'] = vals['mayo_2023']
        linea['junio_2023'] = vals['junio_2023']
        linea['julio_2023'] = vals['julio_2023']
        linea['agosto_2023'] = vals['agosto_2023']
        linea['septiembre_2023'] = vals['septiembre_2023']
        linea['octubre_2023'] = vals['octubre_2023']
        linea['noviembre_2023'] = vals['noviembre_2023']
        linea['diciembre_2023'] = vals['diciembre_2023']
        linea['enero_2024'] = vals['enero_2024']
        linea['febrero_2024'] = vals['febrero_2024']
        linea['marzo_2024'] = vals['marzo_2024']
        linea['abril_2024'] = vals['abril_2024']
        linea['mayo_2024'] = vals['mayo_2024']
        linea['junio_2024'] = vals['junio_2024']
        linea['julio_2024'] = vals['julio_2024']
        linea['agosto_2024'] = vals['agosto_2024']
        linea['septiembre_2024'] = vals['septiembre_2024']
        linea['octubre_2024'] = vals['octubre_2024']
        linea['noviembre_2024'] = vals['noviembre_2024']
        linea['diciembre_2024'] = vals['diciembre_2024']
        return linea

    def _crear_linea_mes(self, concepto, facturas, mes_search, fecha_inicio, fecha_fin):
        linea = {}
        linea['concepto'] = concepto
        
        vals = {
            "enero_2022": 0.0,
            "febrero_2022": 0.0,
            "marzo_2022": 0.0,
            "abril_2022": 0.0,
            "mayo_2022": 0.0,
            "junio_2022": 0.0,
            "julio_2022": 0.0,
            "agosto_2022": 0.0,
            "septiembre_2022": 0.0,
            "octubre_2022": 0.0,
            "noviembre_2022": 0.0,
            "diciembre_2022": 0.0,
            
            "enero_2023": 0.0,
            "febrero_2023": 0.0,
            "marzo_2023": 0.0,
            "abril_2023": 0.0,
            "mayo_2023": 0.0,
            "junio_2023": 0.0,
            "julio_2023": 0.0,
            "agosto_2023": 0.0,
            "septiembre_2023": 0.0,
            "octubre_2023": 0.0,
            "noviembre_2023": 0.0,
            "diciembre_2023": 0.0,
            
            "enero_2024": 0.0,
            "febrero_2024": 0.0,
            "marzo_2024": 0.0,
            "abril_2024": 0.0,
            "mayo_2024": 0.0,
            "junio_2024": 0.0,
            "julio_2024": 0.0,
            "agosto_2024": 0.0,
            "septiembre_2024": 0.0,
            "octubre_2024": 0.0,
            "noviembre_2024": 0.0,
            "diciembre_2024": 0.0,
        }
        
        
        # variable para menejar validacion por mes y año
        date_alt = fecha_inicio

        while date_alt <= fecha_fin:
            fecha_final = fecha_inicio + relativedelta(months=1)
            fac_mes = facturas.filtered(lambda fac_mes: fac_mes.invoice_date_due >= fecha_inicio and fac_mes.invoice_date_due < fecha_final)
            if fac_mes:
                for factura in fac_mes:
                    pagos = json.loads(factura.invoice_payments_widget)
                    if pagos:
                        for pago in pagos['content']:
                            if pago['journal_name'] != 'NDC':
                                datetimeobj=datetime.datetime.strptime(pago['date'],"%Y-%m-%d")
                                if  datetimeobj.month  == mes_search and  datetimeobj.date()  >= fecha_inicio:
                                    if date_alt.month  == 1:
                                        vals[f"enero_{date_alt.year}"] += pago['amount']
                                    elif date_alt.month == 2:
                                        vals[f"febrero_{date_alt.year}"] += pago['amount']
                                    elif date_alt.month == 3:
                                        vals[f"marzo_{date_alt.year}"] += pago['amount']
                                    elif date_alt.month == 4:
                                        vals[f"abril_{date_alt.year}"] += pago['amount']
                                    elif date_alt.month == 5:
                                        vals[f"mayo_{date_alt.year}"] += pago['amount']
                                    elif date_alt.month == 6:
                                        vals[f"junio_{date_alt.year}"] += pago['amount']
                                    elif date_alt.month == 7:
                                        vals[f"julio_{date_alt.year}"] += pago['amount']
                                    elif date_alt.month == 8:
                                        vals[f"agosto_{date_alt.year}"] += pago['amount']
                                    elif date_alt.month == 9:
                                        vals[f"septiembre_{date_alt.year}"] += pago['amount']
                                    elif date_alt.month == 10:
                                        vals[f"octubre_{date_alt.year}"] += pago['amount']
                                    elif date_alt.month == 11:
                                        vals[f"noviembre_{date_alt.year}"] += pago['amount']
                                    elif date_alt.month == 12:
                                        vals[f"diciembre_{date_alt.year}"] += pago['amount']

            fecha_inicio = fecha_final
            # mes += 1
            date_alt = date_alt + relativedelta(months=1)
         
        linea['enero_2022'] = -1 * vals['enero_2022']
        linea['febrero_2022'] = -1 * vals['febrero_2022']
        linea['marzo_2022'] = -1 * vals['marzo_2022']
        linea['abril_2022'] = -1 * vals['abril_2022']
        linea['mayo_2022'] = -1 * vals['mayo_2022']
        linea['junio_2022'] = -1 * vals['junio_2022']
        linea['julio_2022'] = -1 * vals['julio_2022']
        linea['agosto_2022'] = -1 * vals['agosto_2022']
        linea['septiembre_2022'] = -1 * vals['septiembre_2022']
        linea['octubre_2022'] = -1 * vals['octubre_2022']
        linea['noviembre_2022'] = -1 * vals['noviembre_2022']
        linea['diciembre_2022'] = -1 * vals['diciembre_2022']
        linea['enero_2023'] = -1 * vals['enero_2023']
        linea['febrero_2023'] = -1 * vals['febrero_2023']
        linea['marzo_2023'] = -1 * vals['marzo_2023']
        linea['abril_2023'] = -1 * vals['abril_2023']
        linea['mayo_2023'] = -1 * vals['mayo_2023']
        linea['junio_2023'] = -1 * vals['junio_2023']
        linea['julio_2023'] = -1 * vals['julio_2023']
        linea['agosto_2023'] = -1 * vals['agosto_2023']
        linea['septiembre_2023'] = -1 * vals['septiembre_2023']
        linea['octubre_2023'] = -1 * vals['octubre_2023']
        linea['noviembre_2023'] = -1 * vals['noviembre_2023']
        linea['diciembre_2023'] = -1 * vals['diciembre_2023']
        linea['enero_2024'] = -1 * vals['enero_2024']
        linea['febrero_2024'] = -1 * vals['febrero_2024']
        linea['marzo_2024'] = -1 * vals['marzo_2024']
        linea['abril_2024'] = -1 * vals['abril_2024']
        linea['mayo_2024'] = -1 * vals['mayo_2024']
        linea['junio_2024'] = -1 * vals['junio_2024']
        linea['julio_2024'] = -1 * vals['julio_2024']
        linea['agosto_2024'] = -1 * vals['agosto_2024']
        linea['septiembre_2024'] = -1 * vals['septiembre_2024']
        linea['octubre_2024'] = -1 * vals['octubre_2024']
        linea['noviembre_2024'] = -1 * vals['noviembre_2024']
        linea['diciembre_2024'] = -1 * vals['diciembre_2024']
        return linea

class SaldoPorCobrarLinea(models.Model):
    _name = 'saldos.xcobrar.linea'
    _description = 'Linea de saldos por cobrar'

    diario_id = fields.Many2one(string='Diario de saldos por cobrar', comodel_name='rep.diario.saldos.xcobrar', ondelete='cascade')
    concepto = fields.Char(string='Concepto')
    
    # Meses 2022
    enero_2022 = fields.Float(string='Enero 2022')
    febrero_2022 = fields.Float(string='Febrero 2022')
    marzo_2022 = fields.Float(string='Marzo 2022')
    abril_2022 = fields.Float(string='Abril 2022')
    mayo_2022 = fields.Float(string='Mayo 2022')
    junio_2022 = fields.Float(string='Junio 2022')
    julio_2022 = fields.Float(string='Julio 2022')
    agosto_2022 = fields.Float(string='Agosto 2022')
    septiembre_2022 = fields.Float(string='Septiembre 2022')
    octubre_2022 = fields.Float(string='Octubre 2022')
    noviembre_2022 = fields.Float(string='Noviembre 2022')
    diciembre_2022 = fields.Float(string='Diciembre 2022')
    
    # Meses 2023
    enero_2023 = fields.Float(string='Enero 2023')
    febrero_2023 = fields.Float(string='Febrero 2023')
    marzo_2023 = fields.Float(string='Marzo 2023')
    abril_2023 = fields.Float(string='Abril 2023')
    mayo_2023 = fields.Float(string='Mayo 2023')
    junio_2023 = fields.Float(string='Junio 2023')
    julio_2023 = fields.Float(string='Julio 2023')
    agosto_2023 = fields.Float(string='Agosto 2023')
    septiembre_2023 = fields.Float(string='Septiembre 2023')
    octubre_2023 = fields.Float(string='Octubre 2023')
    noviembre_2023 = fields.Float(string='Noviembre 2023')
    diciembre_2023 = fields.Float(string='Diciembre 2023')
    
    # Meses 2024
    enero_2024 = fields.Float(string='Enero 2024')
    febrero_2024 = fields.Float(string='Febrero 2024')
    marzo_2024 = fields.Float(string='Marzo 2024')
    abril_2024 = fields.Float(string='Abril 2024')
    mayo_2024 = fields.Float(string='Mayo 2024')
    junio_2024 = fields.Float(string='Junio 2024')
    julio_2024 = fields.Float(string='Julio 2024')
    agosto_2024 = fields.Float(string='Agosto 2024')
    septiembre_2024 = fields.Float(string='Septiembre 2024')
    octubre_2024 = fields.Float(string='Octubre 2024')
    noviembre_2024 = fields.Float(string='Noviembre 2024')
    diciembre_2024 = fields.Float(string='Diciembre 2024')

class desgloseOrdenesLinea(models.Model):
    _name = 'desglose.ordenes.linea'
    _description = 'Linea de desglose de ordenes'

    concepto = fields.Char(string='Mes')
    date_order = fields.Date(string='Fecha')
    date_order_due = fields.Date(string='Fecha de vencimiento')
    order_folio = fields.Char(string='Ref. nota')
    partner_id = fields.Many2one('res.partner', string='Cliente')
    amount_total = fields.Float(string='Total', digits=(14,2))

class desgloseFacturasLinea(models.Model):
    _name = 'desglose.facturas.linea'
    _description = 'Linea de desglose de facturas'

    concepto = fields.Char(string='Mes')
    name = fields.Char(string='Numero')
    l10n_mx_edi_cfdi_uuid = fields.Char(string='Folio Fiscal')
    invoice_partner_display_name = fields.Char(string='	Nombre del partner')
    invoice_date = fields.Date(string='Fecha de la factura')
    invoice_date_due = fields.Date(string='Fecha de vencimiento')
    amount_total = fields.Float(string='Total', digits=(14,2))
    amount_residual_signed = fields.Float(string='Importe pendiente', digits=(14,2))
    edi_state = fields.Selection(string='Facturación electrónica', selection=[('to_send', 'Por enviar'), ('sent', 'Enviado'), ('to_cancel', 'Por cancelar'), ('cancelled', 'Cancelado')])
    payment_state = fields.Selection(string='Estado de pago', selection=[('not_paid', 'No pagado'), ('in_payment', 'En proceso de pago'), ('paid', 'Pagado'), ('partial', 'Pagado parcialmente'), ('reversed', 'Revertido'), ('invoicing_legacy', 'Sistema anterior de facturación')])
    state = fields.Selection(string='Estado', selection=[('drafr', 'Borrador'), ('posted', 'Publicado'), ('cancel', 'Cancelado')])
    

    #  Values of invoice_payments_widget
    #     "title": "Menos pagos", 
    #     "outstanding": false, 
    #     "content": [
    #         {"name": "", 
    #         "journal_name": "Point of Sale", 
    #         "amount": 27102.190000000002, 
    #         "currency": "$", 
    #         "digits": [69, 2], 
    #         "position": "before", 
    #         "date": "2022-02-08", 
    #         "payment_id": 1032692, 
    #         "partial_id": 26292, "account_payment_id": false, "payment_method_name": null, "move_id": 451983, "ref": "RPOSS/2022/02/0004 (Reversi\u00f3n de: POSS/2022/02/0004)"}]}
