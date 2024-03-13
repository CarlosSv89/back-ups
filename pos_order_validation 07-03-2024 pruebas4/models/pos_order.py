# from odoo import models, fields, api
# from dateutil.relativedelta import relativedelta
# from datetime import datetime

# class PosOrder(models.Model):
#   _inherit = 'pos.order'
  
#   @api.model
#   def _get_current_month(self):
#     today = fields.Date.today()
#     start_date = today + relativedelta(day=1)
#     end_date = today + relativedelta(day=1, months=+1, days=-1)
#     return [('date_order', '>=', start_date), ('date_order', '<', end_date)]
  
#   @api.model
#   def search_read(self, domain=None, limit=None, order=None, count=False):
#     if self._context.get('current_month'):
#       domain = self._get_current_month()
#     return super(PosOrder, self).search_read(domain=domain, limit=limit, order=order, count=count)