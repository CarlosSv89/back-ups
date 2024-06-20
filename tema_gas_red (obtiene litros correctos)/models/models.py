# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.tools import float_round
import logging
_logger = logging.getLogger(__name__)
class PosSession(models.Model):
  _inherit = "pos.session"
  _description = "inheriting pos.session"
  
  @api.onchange('total_lt')
  def log_pos_session(self):
    for line in self:
      _logger.warning(f"litros: {line.total_lt}")

  def get_full_lt(self):
    total_lt = 0.00
    orders_data = self.env['pos.order'].search([('session_id', 'in', self.ids)])
    _logger.info(orders_data)
    for order in orders_data:
        if order.payment_ids:
            for line in order.lines:
                if line.product_id.product_tmpl_id.uom_id.name.upper() == 'KG':
                    total_lt += (line.qty / 0.54)
                if line.product_id.product_tmpl_id.uom_id.name.upper() == 'LT':
                    total_lt += line.qty
                if line.product_id.product_tmpl_id.uom_id.name.upper() == 'UNITS':
                    if line.product_id.product_tmpl_id.qty_contents:
                        total_lt += ((line.qty * line.product_id.product_tmpl_id.qty_contents) / 0.54)
            _logger.info(total_lt)
    return float_round(total_lt, precision_digits=2, precision_rounding=None)
  