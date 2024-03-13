from odoo import models, fields, api, _
import logging
_logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# New sent button to open the payment register wizzard if the policy is PUE 
# ---------------------------------------------------------------------------
class AccountMove(models.Model):
  _inherit = 'account.move'
  
  def open_wizzard(self):
    # Timbrado
    self.action_process_edi_web_services()
    for rec in self:
      # Check for the payment term and the payment policy
      if rec.invoice_payment_term_id.name == 'Pago inmediato' and rec.invoice_date and rec.l10n_mx_edi_payment_policy == 'PUE' and rec.amount_residual > 0:
        # ref to search the view id (integer)
        view_id = self.env.ref('factura_pago_inmediato.account_payment_register_view_form_inherit').id
        # External id of the view
        _logger.warning(f"id => {view_id}")
        # Method to open the payment register wizard, this method is called when the button is pressed
        return {
          'name': _('Register Payment'),
          'res_model': 'account.payment.register',
          'view_mode': 'form',
          'view_id': view_id,
          'context': {
              'active_model': 'account.move',
              'active_ids': self.ids,
              'dont_redirect_to_payments': True,
          },
          'target': 'new',
          'type': 'ir.actions.act_window',
        }


# ----------------------------------------------------
# Setting the payment type in the payment register 
# ----------------------------------------------------

class AccountPayment(models.Model):
  _inherit = 'account.payment'

  x_studio_tipo_de_pago = fields.Selection(selection=[('Cobranza', 	'Cobranza'), ('Contado', 'Contado'), ('Pago anticipado', 'Pago anticipado')], string='Tipo de pago', compute='_get_payment_type', store=True, default='Contado')
  
  # Search for the invoice and get the payment policy
  @api.depends('ref')
  def _get_payment_type(self):
    _logger.warning('------------------------_get_payment_type------------------------')
    for rec in self:
      if rec.ref:
        factura = self.env['account.move'].search([('name', '=', rec.ref)])
        _logger.warning(factura.l10n_mx_edi_payment_policy)
        if factura.l10n_mx_edi_payment_policy == 'PUE':
          rec.x_studio_tipo_de_pago = 'Contado'
        else:
          rec.x_studio_tipo_de_pago = 'Cobranza'
          
# Add l10n_mx_edi_payment_method_id to the payment register, with this you can add the field to your view
class AccountPaymentRegister(models.TransientModel):
  _inherit = 'account.payment.register'
  
  l10n_mx_edi_payment_method_id = fields.Many2one('l10n_mx_edi.payment.method', string='Forma de pago')
  