from odoo import fields,models,api

class AccountMove(models.Model):
  _inherit = 'account.move'
  
  
  # Trying to modify the method _get_reconciled_info_JSON_values 
  def _get_reconciled_info_JSON_values(self):
    self.ensure_one()

    reconciled_vals = []
    for partial, amount, counterpart_line in self._get_reconciled_invoices_partials():
        if counterpart_line.move_id.ref:
            reconciliation_ref = '%s (%s)' % (counterpart_line.move_id.name, counterpart_line.move_id.ref)
        else:
            reconciliation_ref = counterpart_line.move_id.name

        reconciled_vals.append({
            'name': counterpart_line.name,
            'journal_name': counterpart_line.journal_id.name,
            'amount': amount,
            'currency': self.currency_id.symbol,
            'digits': [69, self.currency_id.decimal_places],
            'position': self.currency_id.position,
            'date': counterpart_line.date,
            'payment_id': counterpart_line.id,
            'partial_id': partial.id,
            'account_payment_id': counterpart_line.payment_id.id,
            'payment_method_name': counterpart_line.payment_id.payment_method_id.name if counterpart_line.journal_id.type == 'bank' else None,
            'move_id': counterpart_line.move_id.id,
            'ref': reconciliation_ref,
            'move_type': counterpart_line.move_id.move_type,
        })
    return reconciled_vals