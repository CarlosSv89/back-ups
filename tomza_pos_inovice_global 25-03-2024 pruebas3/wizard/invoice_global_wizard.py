# -*- encoding: utf-8 -*-
##################################################################################################
#
#   Author: Experts SRL de CV (https://exdoo.mx)
#   Coded by: Carlos Blanco (carlos.blanco@exdoo.mx)
#   License: https://blog.exdoo.mx/licencia-de-uso-de-software/
#
##################################################################################################

from odoo import api, fields, models, _
import time
from odoo.exceptions import UserError
from datetime import datetime, timedelta
from pytz import timezone

class InvoiceGlobalWizard(models.TransientModel):
    _inherit = "invoice.global.wizard"

    date_invoice = fields.Datetime('Fecha de Factura', default=fields.Datetime.now)

    @api.model
    def _l10n_mx_edi_get_cfdi_partner_timezone(self, partner):
        code = partner.state_id.code

        # northwest area
        if code == 'BCN':
            return timezone('America/Tijuana')
        # Southeast area
        elif code == 'ROO':
            return timezone('America/Cancun')
        # Pacific area
        elif code in ('BCS', 'CHH', 'SIN', 'NAY'):
            return timezone('America/Chihuahua')
        # Sonora
        elif code == 'SON':
            return timezone('America/Hermosillo')
        # By default, takes the central area timezone
        return timezone('America/Mexico_City')

    def _prepare_invoice_data(self, inv_type_payment='Banco'):
        vals = super(InvoiceGlobalWizard, self)._prepare_invoice_data(inv_type_payment=inv_type_payment)
        issued_address = self.env.user.company_id.partner_id.commercial_partner_id
        tz = self._l10n_mx_edi_get_cfdi_partner_timezone(issued_address)
        tz_force = self.env['ir.config_parameter'].sudo().get_param('l10n_mx_edi_tz_%s' % self.journal_id.id, default=None)
        if tz_force:
            tz = timezone(tz_force)
        datetime_tz = datetime.now(tz)
        datetime_now = datetime.now()
        datetime_tz = datetime.strptime(datetime_tz.strftime("%Y-%m-%d %H:%M:%S"), '%Y-%m-%d %H:%M:%S')
        diff_datetime = datetime_now - datetime_tz
        tz_hours = int(diff_datetime.seconds//3600)
        date_invoice_tz = self.date_invoice - timedelta(hours=tz_hours)
        date_invoice = date_invoice_tz.strftime("%Y-%m-%d")
        vals.update({'invoice_date': date_invoice,'date_time_sign_inv': date_invoice_tz})
        return vals

    def get_invoice_date_sign(self):
        vals = {}
        issued_address = self.env.user.company_id.partner_id.commercial_partner_id
        tz = self._l10n_mx_edi_get_cfdi_partner_timezone(issued_address)
        tz_force = self.env['ir.config_parameter'].sudo().get_param('l10n_mx_edi_tz_%s' % self.journal_id.id, default=None)
        if tz_force:
            tz = timezone(tz_force)
        datetime_tz = datetime.now(tz)
        datetime_now = datetime.now()
        datetime_tz = datetime.strptime(datetime_tz.strftime("%Y-%m-%d %H:%M:%S"), '%Y-%m-%d %H:%M:%S')
        diff_datetime = datetime_now - datetime_tz
        tz_hours = int(diff_datetime.seconds//3600)
        date_invoice_tz = self.date_invoice - timedelta(hours=tz_hours)
        date_invoice = date_invoice_tz.strftime("%Y-%m-%d")
        vals.update({'invoice_date': date_invoice,'date_time_sign_inv': date_invoice_tz})
        return vals

    def _prepare_invoice_line_by_order(self, tax_group, order):
        line_ids = []
        qty_total = 0.0
        price_subtotal = 0.0
        
        tax_rows = self.env['account.tax']
        for line in order.lines:
            tax_rows |= line.tax_ids_after_fiscal_position
            qty_total += line.qty
            price_subtotal += line.price_subtotal
            uom_id = line.product_uom_id.id
        price_unit = round(price_subtotal/qty_total,2)
       
        # Obtenemos moneda del diario de la factura Global
        currency = self.journal_id.currency_id and self.journal_id.currency_id or self.journal_id.company_id.currency_id
        if currency != order.currency_id:
            price_unit = order.currency_id._convert(price_unit, currency, self.journal_id.company_id)
        # Ontenemos las cuentas para las lineas de la factura
        product_row = self.env['product.template'].search([('type', '=', 'product')], limit=1)
        accounts = product_row.get_product_accounts()
        line_vals = {
            'product_id': False,
            'quantity': qty_total,
            'discount': 0,
            'price_unit': price_unit,
            'name': order.name,
            'tax_ids': [(6, 0, tax_rows.ids)],
            'product_uom_id': uom_id,
            'account_id': accounts['income'].id,
        }
        line_ids.append((0, None, line_vals))
        return line_ids

    def action_create_invoice(self):
        self.ensure_one()
        if not self.partner_id:
            raise UserError(_('Seleccione un cliente para facturar.'))
        if not self.pos_order_ids:
            raise UserError(_('No existen ventas a facturar.'))
        # session_rows = self.env['pos.session']
        new_moves_rows = self.env['account.move']
        new_move_cash = new_move = False
        pos_order_rows = []
        pos_links = ""
        for pos_config_row in self.pos_config_ids:
            pos_links += " <a href=# data-oe-model=pos.order data-oe-id=%d>%s</a>"%(pos_config_row.id,pos_config_row.name)
        pos_order_used_rows = self.env['pos.order']
        if self.type_inv == 'bank':
            if self.sale_inv == 'product':
                # Cremamosreamos Factura Global
                move_vals,pos_order_rows = self._prepare_invoice_vals(inv_type_payment='Banco', pos_add_in_invoice=pos_order_used_rows)
                if pos_order_rows:
                    pos_order_used_rows |= pos_order_rows
            else:
                # Cremamosreamos Factura Global
                move_vals,pos_order_rows = self._prepare_invoice_by_sale_vals(inv_type_payment='Banco', pos_add_in_invoice=pos_order_used_rows)
                if pos_order_rows:
                    pos_order_used_rows |= pos_order_rows
            if move_vals:
                vals_date = self.get_invoice_date_sign()
                new_move = self.env['account.move'].sudo().with_company(self.journal_id.company_id).with_context(default_move_type='out_invoice').create(move_vals)
                new_move.write(vals_date)
                new_moves_rows |= new_move
                message = _("This invoice has been created from the POS: %s") % (pos_links,)
                new_move.message_post(body=message)
                # self.pos_order_ids.write({'account_move_global': new_move.id, 'pos_global': True, 'state': 'invoiced'})           
                # self.pos_order_ids.write({'account_move': new_move.id, 'state': 'invoiced', 'pos_global': True, 'partner_id': self.partner_id.id})
                pos_order_rows.write({'account_move': new_move.id,'account_move_global': new_move.id, 'pos_global': True, 'state': 'invoiced'})
                new_move.sudo().with_company(self.journal_id.company_id).action_post()
        elif self.type_inv == 'cash':
            if not pos_order_used_rows:
                pos_order_used_rows = self.env['pos.order']
            # Creamos Factura Global
            if self.sale_inv == 'product':
                move_cash_vals,pos_order_rows = self._prepare_invoice_vals(inv_type_payment='Efectivo', pos_add_in_invoice=pos_order_used_rows)
            else:
                # Cremamosreamos Factura Global
                move_cash_vals,pos_order_rows = self._prepare_invoice_by_sale_vals(inv_type_payment='Efectivo', pos_add_in_invoice=pos_order_used_rows)
            if move_cash_vals:
                vals_date = self.get_invoice_date_sign()
                new_move_cash = self.env['account.move'].sudo().with_company(self.journal_id.company_id).with_context(default_move_type='out_invoice').create(move_cash_vals)
                new_move_cash.write(vals_date)
                new_moves_rows |= new_move_cash
                message = _("This invoice has been created from the POS: %s") % (pos_links,)
                new_move_cash.message_post(body=message)
                # self.pos_order_ids.write({'account_move_global': new_move.id, 'pos_global': True})
                pos_order_rows.write({'account_move': new_move_cash.id,'account_move_global': new_move_cash.id, 'pos_global': True, 'state': 'invoiced'})
                new_move_cash.sudo().with_company(self.journal_id.company_id).action_post()
        elif self.type_inv == 'cash_bank':
            vals = self._prepare_invoice_data('Banco')
            vals.update({'invoice_line_ids': []})
            if self.env['account.move']._fields.get('l10n_mx_edi_payment_method_id', False):
                try:
                    payment_method_row = self.env['10n_mx_edi.payment.method'].search([('code','=', '01')],limit=1)
                    if payment_method_row:
                        vals.update({'l10n_mx_edi_payment_method_id': payment_method_row.id})
                except:
                    pass
            if self.sale_inv == 'product':
                # Cremamosreamos Factura Global
                move_vals,pos_order_rows = self._prepare_invoice_vals(inv_type_payment='Banco', pos_add_in_invoice=pos_order_used_rows)
                if move_vals:
                    invoice_line_ids = move_vals.get('invoice_line_ids')
                    vals.get('invoice_line_ids').extend(invoice_line_ids)
                if pos_order_rows:
                    pos_order_used_rows |= pos_order_rows
                move_cash_vals,pos_order_rows = self._prepare_invoice_vals(inv_type_payment='Efectivo', pos_add_in_invoice=pos_order_used_rows)
                if move_cash_vals:
                    invoice_line_ids = move_cash_vals.get('invoice_line_ids')
                    vals.get('invoice_line_ids').extend(invoice_line_ids)
                if vals.get('invoice_line_ids'):
                    vals_date = self.get_invoice_date_sign()
                    new_move_cash = self.env['account.move'].sudo().with_company(self.journal_id.company_id).with_context(default_move_type='out_invoice').create(vals)
                    new_move_cash.write(vals_date)
                    new_move_cash.write({'date_time_sign_inv': vals.get('date_time_sign_inv')})
                    new_moves_rows |= new_move_cash
                    message = _("This invoice has been created from the POS: %s") % (pos_links,)
                    new_move_cash.message_post(body=message)
                    # self.pos_order_ids.write({'account_move_global': new_move.id, 'pos_global': True})
                    pos_order_rows.write({'account_move': new_move_cash.id,'account_move_global': new_move_cash.id, 'pos_global': True, 'state': 'invoiced'})
                    new_move_cash.sudo().with_company(self.journal_id.company_id).action_post()
            else:
                # Cremamosreamos Factura Global
                move_vals,pos_order_rows = self._prepare_invoice_by_sale_vals(inv_type_payment='Banco', pos_add_in_invoice=pos_order_used_rows)
                if pos_order_rows:
                    pos_order_used_rows |= pos_order_rows
                if move_vals:
                    invoice_line_ids = move_vals.get('invoice_line_ids')
                    vals.get('invoice_line_ids').extend(invoice_line_ids)
                # Cremamosreamos Factura Global
                move_cash_vals,pos_order_rows = self._prepare_invoice_by_sale_vals(inv_type_payment='Efectivo', pos_add_in_invoice=pos_order_used_rows)
                if move_cash_vals:
                    invoice_line_ids = move_cash_vals.get('invoice_line_ids')
                    vals.get('invoice_line_ids').extend(invoice_line_ids)
                if vals.get('invoice_line_ids'):
                    vals_date = self.get_invoice_date_sign()
                    new_move_cash = self.env['account.move'].sudo().with_company(self.journal_id.company_id).with_context(default_move_type='out_invoice').create(vals)
                    new_move_cash.write(vals_date)
                    new_moves_rows |= new_move_cash
                    message = _("This invoice has been created from the POS: %s") % (pos_links,)
                    new_move_cash.message_post(body=message)
                    # self.pos_order_ids.write({'account_move_global': new_move.id, 'pos_global': True})
                    pos_order_rows.write({'account_move': new_move_cash.id,'account_move_global': new_move_cash.id, 'pos_global': True, 'state': 'invoiced','partner_id': self.partner_id.id})
                    new_move_cash.sudo().with_company(self.journal_id.company_id).action_post()
        # * Se quita la reversa de la factura
        # Reversa de Factura en Banco\
        # if new_move:
        #     reversal_row = self.env['account.move.reversal'].create({'move_ids': [(6,0,new_move.ids)], 'refund_method': 'cancel'})
        #     reversal_row.reverse_moves()
            # new_move.move_type = 'out_invoice'
        # Reversa de Factura en Efectivo
        # if new_move_cash:
        #     reversal_row = self.env['account.move.reversal'].create({'move_ids': [(6,0,new_move_cash.ids)], 'refund_method': 'cancel'})
        #     reversal_row.reverse_moves()
        #     new_move_cash.move_type = 'out_invoice'
        if new_moves_rows:
            invoices = new_moves_rows
            action = self.env["ir.actions.actions"]._for_xml_id("account.action_move_out_invoice_type")
            if len(invoices) > 1:
                action['domain'] = [('id', 'in', invoices.ids)]
            elif len(invoices) == 1:
                form_view = [(self.env.ref('account.view_move_form').id, 'form')]
                if 'views' in action:
                    action['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
                else:
                    action['views'] = form_view
                action['res_id'] = invoices.id
            else:
                action = {'type': 'ir.actions.act_window_close'}

            context = {
                'default_move_type': 'out_invoice',
            }
            action['context'] = context
            return action
        return True
