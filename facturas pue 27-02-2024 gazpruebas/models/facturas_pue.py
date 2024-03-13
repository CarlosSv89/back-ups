# from odoo import models,fields,api

# class Facturas_pue(models.Model):
#   _name = 'reportes_credito.facturas_pue'
#   _description = 'Facturas Pue'

#   fecha_inicial = fields.Date(string='Fecha Inicial')
#   fecha_final = fields.Date(string='Fecha Final')
#   company_id = fields.Many2one(comodel_name='res.company', required=True, default=lambda self: self.env.company)

#   # relacion con la tabla de facturas_pue_line
#   facturas_ids = fields.One2many(comodel_name='facturas.pue.line', inverse_name='factura_id', string='Facturas')

#   @api.onchange('fecha_inicial', 'fecha_final')
#   def _get_facturas_pue(self):
#     for line in self:
#       if line.fecha_inicial and line.fecha_final:
#         self.facturas_ids = [(5, 0, 0)]
#         # buscar las facturas
#         facturas = self.env['account.move'].search([('move_type', '=', 'out_invoice'),('amount_residual_signed', '!=',0),('edi_state','in',['to_send','to_cancel']),('x_studio_tipo', '=', 'Crédito')])
        
#         for rec in facturas:
#           # condicion para filtrar las facturas PUE
#           row = {}
#           row['name'] = rec.name
#           row['l10n_mx_edi_cfdi_uuid'] = rec.l10n_mx_edi_cfdi_uuid
#           row['x_studio_cliente'] = rec.x_studio_cliente
#           row['type_name'] = rec.type_name
#           row['l10n_mx_edi_payment_policy'] = rec.l10n_mx_edi_payment_policy
#           row['canal_distribucion'] = rec.canal_distribucion
#           row['invoice_partner_display_name'] = rec.invoice_partner_display_name
#           row['invoice_payment_term_id'] = rec.invoice_payment_term_id
#           row['invoice_date'] = rec.invoice_date
#           row['invoice_date_due'] = rec.invoice_date_due
#           row['x_studio_tipo'] = rec.x_studio_tipo
#           row['activity_ids'] = rec.activity_ids
#           row['company_id'] = rec.company_id
#           row['amount_untaxed_signed'] = rec.amount_untaxed_signed
#           row['amount_total_signed'] = rec.amount_total_signed
#           row['state'] = rec.state
#           row['payment_state'] = rec.payment_state
#           row['edi_state'] = rec.edi_state
#           row['id'] = rec.id
#           self.facturas_ids = [(0, 0, row)]


# class Facturas_pue_line(models.Model):
#   _name = 'facturas.pue.line'
#   _description = 'Facturas Pue Line'

#   name = fields.Char(string='Numero')
#   l10n_mx_edi_cfdi_uuid = fields.Char(string='Folio fiscal')
#   x_studio_cliente = fields.Char(string='Cliente')
#   type_name = fields.Char(string='Nombre de tipo')
#   l10n_mx_edi_payment_policy = fields.Selection([('PUE', 'PUE'), ('PPD', 'PPD')], string='Política de pago')
#   canal_distribucion = fields.Selection(selection=[('Portátil', 'Portátil'), ('Autotanque', 'Autotanque'), ('Carburación', 'Carburación')], string='Canal de distribución')
#   invoice_partner_display_name = fields.Char(string='Nombre del cliente')
#   invoice_payment_term_id = fields.Char(string='Términos de pago')
#   invoice_date = fields.Date(string='Fecha de factura')
#   invoice_date_due = fields.Date(string='Fecha de vencimiento')
#   x_studio_tipo = fields.Selection([('Crédito', 'Crédito'), ('Contado', 'Contado'), ('Usuario', 'Usuario'), ('Empresa', 'Empresa'), ('Proveedor', 'Proveedor'), ('Otros', 'Otros')], string='Tipo')
#   activity_ids = fields.Char(string='Siguiente actividad')
#   company_id = fields.Many2one(comodel_name='res.company', required=True, default=lambda self: self.env.company)
#   amount_untaxed_signed = fields.Float(string='Importe sin impuesto firmado', digits=(14, 2))
#   amount_total_signed = fields.Float(string='Total firmado', digits=(14, 2))
#   state = fields.Selection([('draft', 'Borrador'), ('posted', 'Publicado'), ('cancel', 'Cancelado')], string='Estado')
#   payment_state = fields.Selection(string='Estado de pago', selection=[('not_paid', 'No pagado'), ('in_payment', 'En proceso de pago'), ('paid', 'Pagado'), ('partial', 'Pagado parcialmente'), ('reversed', 'Revertido'), ('invoicing_legacy', 'Sistema anterior de facturación')])
#   edi_state = fields.Selection(string='Facturación electrónica', selection=[('to_send', 'Por enviar'), ('sent', 'Enviado'), ('to_cancel', 'Por cancelar'), ('cancelled', 'Cancelado')])
#   id = fields.Char(string='Identificacion')

#   factura_id = fields.Many2one('reportes_credito.facturas_pue', string='Factura')

# class AccountMove(models.Model):
#   _inherit = 'account.move'

#   l10n_mx_edi_cfdi_uuid = fields.Char(string="Folio Fiscal")
#   l10n_mx_edi_payment_policy = fields.Selection(string="Política de pago", selection=[('PUE', 'PUE'), ('PPD', 'PPD')])

  # policy_computed = fields.Char(string="Política de pago", compute="_compute_payment_policy", store=True)


  # # computar el campo de politica de pago
  # def _compute_payment_policy(self):
  #   for record in self:
  #     record.policy_computed = record.l10n_mx_edi_payment_policy