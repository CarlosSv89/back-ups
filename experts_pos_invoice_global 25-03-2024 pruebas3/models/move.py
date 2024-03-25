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

class AccountMove(models.Model):
    _inherit = 'account.move'

    pos_global = fields.Boolean('Factura global', default=False)

    def action_cancel_global_invoice_pos(self):
        if self.pos_global:
            # Eliminamos la conciliacion de pagos de la factura
            self.line_ids.sudo().remove_move_reconcile()
            reversal_move_row = self.search([('reversed_entry_id','=', self.id), ('state','=', 'posted')], limit=1)
            if reversal_move_row:
                reversal_move_row.sudo().button_draft()
                reversal_move_row.sudo().button_cancel()
            
            # Buscamos todas las ventas de la factura global
            order_rows = self.env['pos.order'].search([('account_move_global','=', self.id)])
            # # Obtenemos todas las sesiones
            # session_rows = self.env['pos.session']
            # for order_row in order_rows:
            #     session_rows |= order_row.session_id
            # Actualizamos el estado y quitamos el ID de la factura a la venta
            order_rows.write({'account_move_global': False, 'pos_global': False, 'state': 'done', 'account_move': False, 'partner_id': False})
            # for session_row in session_rows:
            #     # Abrimos los statements para editarlos al cerrar
            #     session_row.statement_ids.button_reopen()
            #     # Eliminamos las lineas porque se vuelven a generar a cerrar
            #     for statement_row in session_row.statement_ids:
            #         statement_row.line_ids.unlink()
            #     # Eliminamos el move de la sesion
            #     session_row.move_id.line_ids.remove_move_reconcile()
            #     session_row.move_id.button_draft()
            #     session_row.move_id.button_cancel()
            #     session_row.move_id.with_context(force_delete=True).unlink()
            #     #Cambiamos el estado de la sesion y le quitamos el move
            #     session_row.write({'move_id': False, 'state':'closing_control'})
            #     # Todas las ventas que no estan facturadas las pasamos a pagada para cerrar sesion
            #     session_row.order_ids.filtered(lambda order: order.state == 'done').write({'state':'paid', 'account_move': False})
            #     # Cerramos sesion
            #     session_row.action_pos_session_validate()
        return True

    def button_cancel(self):
        for move_row in self:
            if move_row.pos_global:
                move_row.action_cancel_global_invoice_pos()
        return super(AccountMove,self).button_cancel()

        