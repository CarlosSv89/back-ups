# -*- encoding: utf-8 -*-
##################################################################################################
#
#   Author: Experts SRL de CV (https://exdoo.mx)
#   Coded by: Carlos Blanco (carlos.blanco@exdoo.mx)
#   License: https://blog.exdoo.mx/licencia-de-uso-de-software/
#
##################################################################################################
from odoo import api, fields, models, _, tools, SUPERUSER_ID
from odoo.exceptions import UserError

class PosOrder(models.Model):
    _inherit = 'pos.order'

    pos_global = fields.Boolean('Factura global', default=False, copy=False)
    account_move_global = fields.Many2one('account.move', string='Invoice Global', readonly=True, copy=False)


    def action_view_invoice(self):
        if self.pos_global:
            return {
                'name': _('Customer Invoice'),
                'view_mode': 'form',
                'view_id': self.env.ref('account.view_move_form').id,
                'res_model': 'account.move',
                'context': "{'move_type':'out_invoice'}",
                'type': 'ir.actions.act_window',
                'res_id': self.account_move_global.id,
            }
        else:
            return {
                'name': _('Customer Invoice'),
                'view_mode': 'form',
                'view_id': self.env.ref('account.view_move_form').id,
                'res_model': 'account.move',
                'context': "{'move_type':'out_invoice'}",
                'type': 'ir.actions.act_window',
                'res_id': self.account_move.id,
            }
    