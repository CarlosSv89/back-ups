from odoo import fields,models,api

class AccountMove(models.Model):
  _inherit = 'account.move'

  l10n_mx_edi_cfdi_uuid = fields.Char(string='Folio fiscal')
  l10n_mx_edi_payment_policy = fields.Selection([('PUE', 'PUE'), ('PPD', 'PPD')], string='Política de pago')
  # alt_payment_policy = fields.Selection([('PUE', 'PUE'), ('PPD', 'PPD')], string='Política de pago alternativa')

  # @api.model
  # def update_existing_records(self):
  #   existing_records = self.search([])

  #   for record in existing_records:
  #     print(record.l10n_mx_edi_payment_policy)
  #     record.alt_payment_policy = record.l10n_mx_edi_payment_policy

  #   self.env.cr.commit()