from odoo import models,fields,api

class Facturas_pue(models.Model):
  _name = 'rep_credito.facturas_pue'
  _description = 'Facturas Pue'

  name = fields.Char(string='Facturas PUE', default='Reporte de facturas PUE')
  fecha_inicial = fields.Date(string='Fecha Inicial')
  fecha_final = fields.Date(string='Fecha Final')
  company_id = fields.Many2one(comodel_name='res.company', required=True, default=lambda self: self.env.company)

  # relacion con la tabla de facturas_pue_line
  facturas_ids = fields.Many2many(comodel_name='facturas_pue_line', string='Facturas')

  @api.onchange('fecha_inicial', 'fecha_final')
  def _get_facturas_pue(self):
    for line in self:
      if line.fecha_inicial and line.fecha_final:
        # limpiar las facturas        
        line.facturas_ids = [(5, 0, 0)]

        # buscar las facturas
        facturas = self.env['account.move'].search([('invoice_date', '>=', line.fecha_inicial),('invoice_date_due', '<=', line.fecha_final),('move_type', '=', 'out_invoice'),('edi_state','in',['sent','to_cancel']),('state', '=', 'posted'),('x_studio_tipo', '=', 'Crédito'), ('payment_state', '=', 'not_paid')])
        
        row = {}
        for rec in facturas:
          # condicion para filtrar las facturas PUE y que tengan un saldo pendiente
          if rec.l10n_mx_edi_payment_policy == 'PUE' and rec.amount_residual_signed > 0.00: 
            row['name'] = rec.name
            row['l10n_mx_edi_cfdi_uuid'] = rec.l10n_mx_edi_cfdi_uuid
            row['x_studio_cliente'] = rec.x_studio_cliente
            row['type_name'] = rec.type_name
            row['l10n_mx_edi_payment_policy'] = rec.l10n_mx_edi_payment_policy
            row['canal_distribucion'] = rec.canal_distribucion
            row['invoice_partner_display_name'] = rec.invoice_partner_display_name
            row['invoice_payment_term_id'] = rec.invoice_payment_term_id.name
            row['invoice_date'] = rec.invoice_date
            row['invoice_date_due'] = rec.invoice_date_due
            row['x_studio_tipo'] = rec.x_studio_tipo
            row['activity_ids'] = rec.activity_ids
            row['company_id'] = rec.company_id.display_name
            row['amount_untaxed_signed'] = rec.amount_untaxed_signed
            row['amount_total_signed'] = rec.amount_total_signed
            row['state'] = rec.state
            row['payment_state'] = rec.payment_state
            row['edi_state'] = rec.edi_state
            row['id_factura'] = rec.id
            self.facturas_ids = [(0, 0, row)]


class Facturas_pue_line(models.Model):
  _name = 'facturas_pue_line'
  _description = 'Facturas Pue Line'

  name = fields.Char(string='Número')
  l10n_mx_edi_cfdi_uuid = fields.Char(string='Folio fiscal')
  x_studio_cliente = fields.Char(string='Cliente')
  type_name = fields.Char(string='Nombre de tipo')
  l10n_mx_edi_payment_policy = fields.Selection([('PUE', 'PUE'), ('PPD', 'PPD')], string='Política de pago')
  canal_distribucion = fields.Selection(selection=[('Portátil', 'Portátil'), ('Autotanque', 'Autotanque'), ('Carburación', 'Carburación')], string='Canal de distribución')
  invoice_partner_display_name = fields.Char(string='Nombre del cliente')
  invoice_payment_term_id = fields.Char(string='Términos de pago')
  invoice_date = fields.Date(string='Fecha de factura')
  invoice_date_due = fields.Date(string='Fecha de vencimiento')
  x_studio_tipo = fields.Selection([('Crédito', 'Crédito'), ('Contado', 'Contado'), ('Usuario', 'Usuario'), ('Empresa', 'Empresa'), ('Proveedor', 'Proveedor'), ('Otros', 'Otros')], string='Tipo')
  activity_ids = fields.Char(string='Siguiente actividad')
  company_id = fields.Char(string="Empresa")
  amount_untaxed_signed = fields.Float(string='Importe sin impuesto firmado', digits=(14, 2))
  amount_total_signed = fields.Float(string='Total firmado', digits=(14, 2))
  state = fields.Selection([('draft', 'Borrador'), ('posted', 'Publicado'), ('cancel', 'Cancelado')], string='Estado')
  payment_state = fields.Selection(string='Estado de pago', selection=[('not_paid', 'Sin pagar'), ('in_payment', 'Pagado, sin conciliar'), ('paid', 'Pagado'), ('partial', 'Pagado parcialmente'), ('reversed', 'Revertido'), ('invoicing_legacy', 'Sistema anterior de facturación')])
  edi_state = fields.Selection(string='Facturación electrónica', selection=[('to_send', 'Por enviar'), ('sent', 'Enviado'), ('to_cancel', 'Por cancelar'), ('cancelled', 'Cancelado')])
  id_factura = fields.Integer(string='Identificación')

  # factura_id = fields.Many2one('reportes_credito.facturas_pue', string='Factura')