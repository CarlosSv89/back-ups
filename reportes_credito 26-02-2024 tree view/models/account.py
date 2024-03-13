from odoo import models,fields,api


class AccountMove(models.Model):
  _inherit = 'account.move'

  l10n_mx_edi_cfdi_uuid = fields.Char(string="Folio Fiscal")
  l10n_mx_edi_payment_policy = fields.Selection(string="Política de pago", selection=[('PUE', 'PUE'), ('PPD', 'PPD')])