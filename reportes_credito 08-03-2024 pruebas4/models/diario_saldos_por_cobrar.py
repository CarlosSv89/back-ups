import datetime
import calendar
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
import json
import locale

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
        enero = 0.0
        febrero = 0.0
        marzo = 0.0
        abril = 0.0
        mayo = 0.0
        junio = 0.0
        julio = 0.0
        agosto = 0.0
        septiembre = 0.0
        octubre = 0.0
        noviembre = 0.0
        diciembre = 0.0

        mes = fecha_inicio.month

        while mes <= fecha_fin.month:
            fecha_final = fecha_inicio + relativedelta(months=1)
            fac_mes = facturas.filtered(lambda fac_mes: fac_mes.invoice_date_due >= fecha_inicio and fac_mes.invoice_date_due < fecha_final)
            for factura in fac_mes:
                pagos = json.loads(factura.invoice_payments_widget)
                if pagos:
                    for pago in pagos['content']:
                        if pago['journal_name'] != 'NDC':
                            datetimeobj=datetime.datetime.strptime(pago['date'],"%Y-%m-%d")
                            if datetimeobj.date() < fecha_inicio:
                                if mes == 1: #Contabilizar facturas de enero
                                    enero += pago['amount']
                                elif mes == 2: #Contabilizar facturas de febrero
                                    febrero += pago['amount']
                                elif mes == 3: #Contabilizar facturas de marzo
                                    marzo += pago['amount']
                                elif mes == 4: #Contabilizar facturas de abril
                                    abril += pago['amount']
                                elif mes == 5: #Contabilizar facturas de mayo
                                    mayo += pago['amount']
                                elif mes == 6: #Contabilizar facturas de junio
                                    junio += pago['amount']
                                elif mes == 7: #Contabilizar facturas de julio
                                    julio += pago['amount']
                                elif mes == 8: #Contabilizar facturas de agosto
                                    agosto += pago['amount']
                                elif mes == 9: #Contabilizar facturas de septiembre
                                    septiembre += pago['amount']
                                elif mes == 10: #Contabilizar facturas de octubre
                                    octubre += pago['amount']
                                elif mes == 11: #Contabilizar facturas de noviembre
                                    noviembre += pago['amount']
                                elif mes == 12: #Contabilizar facturas de diciembre
                                    diciembre += pago['amount']
            fecha_inicio = fecha_final
            mes += 1
        
        linea['enero'] = -1 * enero
        linea['febrero'] = -1 * febrero
        linea['marzo'] = -1 * marzo
        linea['abril'] = -1 * abril
        linea['mayo'] = -1 * mayo
        linea['junio'] = -1 * junio
        linea['julio'] = -1 * julio
        linea['agosto'] = -1 * agosto
        linea['septiembre'] = -1 * septiembre
        linea['octubre'] = -1 * octubre
        linea['noviembre'] = -1 * noviembre
        linea['diciembre'] = -1 * diciembre
        return linea

    def _crear_linea_descuentos(self, concepto, facturas, fecha_inicio, fecha_fin):
        linea = {}
        linea['concepto'] = concepto
        enero = 0.0
        febrero = 0.0
        marzo = 0.0
        abril = 0.0
        mayo = 0.0
        junio = 0.0
        julio = 0.0
        agosto = 0.0
        septiembre = 0.0
        octubre = 0.0
        noviembre = 0.0
        diciembre = 0.0

        mes = fecha_inicio.month

        while mes <= fecha_fin.month:
            fecha_final = fecha_inicio + relativedelta(months=1)
            notas = self.env['account.move'].search([("invoice_date_due",">=",fecha_inicio),("invoice_date_due","<=",fecha_final), ('state', '=', 'posted'),
                                                            ('move_type', '=', 'out_refund'), ('edi_state','=','sent'), ('payment_state', '=', 'paid')])
            fac_mes = facturas.filtered(lambda fac_mes: fac_mes.invoice_date_due >= fecha_inicio and fac_mes.invoice_date_due < fecha_final)
            if fac_mes:
                for factura in fac_mes:
                    descuentos = json.loads(factura.invoice_payments_widget)
                    if descuentos:
                        for nota in descuentos['content']:
                            if nota['payment_id'] == '1846310':
                                # datetimeobj=datetime.datetime.strptime(nota['date'],"%Y-%m-%d")
                                # if  datetimeobj.month  == mes_search and  datetimeobj.date()  >= fecha_inicio:
                                if mes  == 1:
                                    enero += nota['amount']
                                elif mes == 2:
                                    febrero += nota['amount']
                                elif mes == 3:
                                    marzo += nota['amount']
                                elif mes == 4:
                                    abril += nota['amount']
                                elif mes == 5:
                                    mayo += nota['amount']
                                elif mes == 6:
                                    junio += nota['amount']
                                elif mes == 7:
                                    julio += nota['amount']
                                elif mes == 8:
                                    agosto += nota['amount']
                                elif mes == 9:
                                    septiembre += nota['amount']
                                elif mes == 10:
                                    octubre += nota['amount']
                                elif mes == 11:
                                    noviembre += nota['amount']
                                elif mes == 12:
                                    diciembre += nota['amount']

            fecha_inicio = fecha_final
            mes += 1
         
        linea['enero'] = -1 * enero
        linea['febrero'] = -1 * febrero
        linea['marzo'] = -1 * marzo
        linea['abril'] = -1 * abril
        linea['mayo'] = -1 * mayo
        linea['junio'] = -1 * junio
        linea['julio'] = -1 * julio
        linea['agosto'] = -1 * agosto
        linea['septiembre'] = -1 * septiembre
        linea['octubre'] = -1 * octubre
        linea['noviembre'] = -1 * noviembre
        linea['diciembre'] = -1 * diciembre
        return linea


    def _crear_linea_meta(self, concepto, facturas, ordenes, fecha_inicio, fecha_fin):
        linea = {}
        linea['concepto'] = concepto
        enero = 0.0
        febrero = 0.0
        marzo = 0.0
        abril = 0.0
        mayo = 0.0
        junio = 0.0
        julio = 0.0
        agosto = 0.0
        septiembre = 0.0
        octubre = 0.0
        noviembre = 0.0
        diciembre = 0.0
        
        linea_facturas = {}
        linea_ordenes = {}       
        mes = fecha_inicio.month

        while mes <= fecha_fin.month:
            fecha_final = fecha_inicio + relativedelta(months=1)
            if fecha_inicio == fecha_fin:
                f = facturas.filtered(lambda f: f.invoice_date_due == fecha_inicio)
            else:
                f = facturas.filtered(lambda f: f.invoice_date_due >= fecha_inicio and f.invoice_date_due < fecha_final)

            for factura in f:
                if mes == 1:
                    enero += factura.amount_total_signed
                if mes == 2:
                    febrero += factura.amount_total_signed
                if mes == 3:
                    marzo += factura.amount_total_signed
                if mes == 4:
                    abril += factura.amount_total_signed
                if mes == 5:
                    mayo += factura.amount_total_signed
                if mes == 6:
                    junio += factura.amount_total_signed
                if mes == 7:
                    julio += factura.amount_total_signed
                if mes == 8:
                    agosto += factura.amount_total_signed
                if mes == 9:
                    septiembre += factura.amount_total_signed
                if mes == 10:
                    octubre += factura.amount_total_signed
                if mes == 11:
                    noviembre += factura.amount_total_signed
                if mes == 12:
                    diciembre += factura.amount_total_signed

                # Facturas residual(no pagadas)
                if factura.amount_residual_signed != 0.00:
                    linea_facturas['concepto'] = calendar.month_name[mes]
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
                        if mes == 1:
                            enero += order_vencida.amount_total
                        if mes == 2:
                            febrero += order_vencida.amount_total
                        if mes == 3:
                            marzo += order_vencida.amount_total
                        if mes == 4:
                            abril += order_vencida.amount_total
                        if mes == 5:
                            mayo += order_vencida.amount_total
                        if mes == 6:
                            junio += order_vencida.amount_total
                        if mes == 7:
                            julio += order_vencida.amount_total
                        if mes == 8:
                            agosto += order_vencida.amount_total
                        if mes == 9:
                            septiembre += order_vencida.amount_total
                        if mes == 10:
                            octubre += order_vencida.amount_total
                        if mes == 11:
                            noviembre += order_vencida.amount_total
                        if mes == 12:
                            diciembre += order_vencida.amount_total

                        # Ordenes de credito(no se han facturado)
                        linea_ordenes['concepto'] = calendar.month_name[mes]
                        linea_ordenes['date_order'] = order_vencida.date_order.date()
                        linea_ordenes['date_order_due'] = order_vencida_due.date()
                        linea_ordenes['order_folio'] = order_vencida.order_folio
                        linea_ordenes['partner_id'] = order_vencida.partner_id
                        linea_ordenes['amount_total'] = order_vencida.amount_total

                        self.linea_desglose_ordenes = [(0,0,linea_ordenes)]

            fecha_inicio = fecha_final
            mes += 1

        linea['enero'] = enero
        linea['febrero'] = febrero
        linea['marzo'] = marzo
        linea['abril'] = abril
        linea['mayo'] = mayo
        linea['junio'] = junio
        linea['julio'] = julio
        linea['agosto'] = agosto
        linea['septiembre'] = septiembre
        linea['octubre'] = octubre
        linea['noviembre'] = noviembre
        linea['diciembre'] = diciembre
        return linea

    def _crear_linea_mes(self, concepto, facturas, mes_search, fecha_inicio, fecha_fin):
        linea = {}
        linea['concepto'] = concepto
        enero = 0.0
        febrero = 0.0
        marzo = 0.0
        abril = 0.0
        mayo = 0.0
        junio = 0.0
        julio = 0.0
        agosto = 0.0
        septiembre = 0.0
        octubre = 0.0
        noviembre = 0.0
        diciembre = 0.0

        mes = fecha_inicio.month

        while mes <= fecha_fin.month:
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
                                    if mes  == 1:
                                        enero += pago['amount']
                                    elif mes == 2:
                                        febrero += pago['amount']
                                    elif mes == 3:
                                        marzo += pago['amount']
                                    elif mes == 4:
                                        abril += pago['amount']
                                    elif mes == 5:
                                        mayo += pago['amount']
                                    elif mes == 6:
                                        junio += pago['amount']
                                    elif mes == 7:
                                        julio += pago['amount']
                                    elif mes == 8:
                                        agosto += pago['amount']
                                    elif mes == 9:
                                        septiembre += pago['amount']
                                    elif mes == 10:
                                        octubre += pago['amount']
                                    elif mes == 11:
                                        noviembre += pago['amount']
                                    elif mes == 12:
                                        diciembre += pago['amount']

            fecha_inicio = fecha_final
            mes += 1
         
        linea['enero'] = -1 * enero
        linea['febrero'] = -1 * febrero
        linea['marzo'] = -1 * marzo
        linea['abril'] = -1 * abril
        linea['mayo'] = -1 * mayo
        linea['junio'] = -1 * junio
        linea['julio'] = -1 * julio
        linea['agosto'] = -1 * agosto
        linea['septiembre'] = -1 * septiembre
        linea['octubre'] = -1 * octubre
        linea['noviembre'] = -1 * noviembre
        linea['diciembre'] = -1 * diciembre
        return linea

      
class SaldoPorCobrarLinea(models.Model):
    _name = 'saldos.xcobrar.linea'
    _description = 'Linea de saldos por cobrar'

    diario_id = fields.Many2one(string='Diario de saldos por cobrar', comodel_name='rep.diario.saldos.xcobrar', ondelete='cascade')
    concepto = fields.Char(string='Concepto')
    enero = fields.Float(string='Enero')
    febrero = fields.Float(string='Febrero')
    marzo = fields.Float(string='Marzo')
    abril = fields.Float(string='Abril')
    mayo = fields.Float(string='Mayo')
    junio = fields.Float(string='Junio')
    julio = fields.Float(string='Julio')
    agosto = fields.Float(string='Agosto')
    septiembre = fields.Float(string='Septiembre')
    octubre = fields.Float(string='Octubre')
    noviembre = fields.Float(string='Noviembre')
    diciembre = fields.Float(string='Diciembre')

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
