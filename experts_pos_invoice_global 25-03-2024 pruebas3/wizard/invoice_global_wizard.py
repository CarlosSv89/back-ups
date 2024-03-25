# -*- encoding: utf-8 -*-
##################################################################################################
#
#   Author: Experts SRL de CV (https://exdoo.mx)
#   Coded by: Daniel Acosta (daniel.acosta@exdoo.mx)
#   License: https://blog.exdoo.mx/licencia-de-uso-de-software/
#
##################################################################################################

from odoo import api, fields, models, _
import time
from odoo.exceptions import UserError
from datetime import datetime, timedelta
from pytz import timezone

class InvoiceGlobalWizard(models.TransientModel):
    _name = "invoice.global.wizard"
    _description = 'Asistente de factura global para POS'

    def _get_uom_act(self):
        try:
            uom_sat_row = self.env['clave.prod.uom'].search([('clave','=', 'ACT')],limit=1)
            if uom_sat_row:
                uom_row = self.env['uom.uom'].search([('claveuni_id', '=', uom_sat_row.id)], limit=1)
                return uom_row and uom_row.id or False
        except:
            return False
        return False

    # pos_config_id = fields.Many2one('pos.config', 'Elija un punto de venta', required=False)
    pos_config_ids = fields.Many2many('pos.config', string='Elija los puntos de venta', required=True)
    # pos_config_ids = fields.Many2many('pos.config', 'wizard_pos_config_rel', 'wizard_id', 'pos_config_id', string='Elija los puntos de venta', required=True)
    date_start = fields.Date('Fecha inicio', required=True)
    date_end = fields.Date('Fecha final', required=True)
    partner_id = fields.Many2one('res.partner', 'Cliente', required=True)
    pos_order_ids = fields.Many2many('pos.order','invglobal_order_rel','inv_global_id','order_id','Ventas')
    payment_bank = fields.Float('Pago a banco', default=0.0)
    payment_cash = fields.Float('Pago a efectivo', default=0.0)
    amount = fields.Float('Monto a facturar', default=0.0)
    type_inv = fields.Selection([('cash','Efectivo'),('bank', 'Banco'),('cash_bank', 'Banco y Efectivo')], 'Tipo de Factura', readonly=False, copy=False, default='cash_bank', help="Efectivo: Al seleccionar esta opción, solo se creara una factura con las ventas que tengan pago en efectivo. No se podra facturar mas del monto indicado.\nBanco: Al seleccionar esta opción solo se creara una factura con las ventas que tengan pago no se a efectivo.\nEfectivo y Banco: Al seleccionar esta opción se crearan 2 facturas si es necesario primero se creara una factura con el las ventas pagadas con pagas que no son efectivo y si aun se tiene monto a facturar, se crea una factura con ventas pagadas en efectivo.")
    # session_select = fields.Selection([('one','Solo un punto de venta'),('all', 'Todos los puntos de venta')], '', readonly=False, copy=False, default='cash_bank', help="Solo un punto de venta: Al seleccionar esta opción se podra elegir un TPV para generar la factura global solo de esas ventas. La configuración para crear la factura se toman de la TPV seleccionado.\nTodos los puntos de venta: Al seleccionar esta opción se creara una factura global de todos los puntos de venta del sistema")
    journal_id = fields.Many2one('account.journal', 'Diario de ventas', required=True)
    sale_inv = fields.Selection([('product','Producto'),('sale', 'Venta')], 'Forma de Facturacion', readonly=False, copy=False, default='product', help="Producto: La factura globla mostrara los productos conteninos en las ventas seleccionadas. Venta: La factura global mostrara las ventas como descripciones.")
    uom_id = fields.Many2one('uom.uom', 'Unidad de medida', help=u'Unidad de medida asignada a las líneas de factura global por ventas', default=_get_uom_act)


    def _get_time_zone(self):
        res_users_obj = self.env['res.users']
        userstz = res_users_obj.browse(self._uid).tz
        a = 0
        if userstz:
            hours = timezone(userstz)
            fmt = '%Y-%m-%d %H:%M:%S %Z%z'
            now = datetime.now()
            loc_dt = hours.localize(datetime(now.year, now.month, now.day,
                                             now.hour, now.minute, now.second))
            timezone_loc = (loc_dt.strftime(fmt))
            diff_timezone_original = timezone_loc[-5:-2]
            timezone_original = int(diff_timezone_original)
            s = str(datetime.now(timezone(userstz)))
            s = s[-6:-3]
            timezone_present = int(s)*-1
            a = timezone_original + ((
                timezone_present + timezone_original)*-1)
        return a

    def get_pos_amounts(self):
        amount = 0.0
        amount_cash = 0.0
        if self.pos_config_ids and self.date_start and self.date_end:
            # Obtenemos el inicio y fin con hora y zona horaria del usuario
            time_zone = self._get_time_zone()
            # Obtenemos la fecha con 00:00 y 23:59
            date_start = self.date_start.strftime("%Y/%m/%d")
            date_end = self.date_end.strftime("%Y/%m/%d")
            date_start = date_start + ' 00:00:00'
            date_end = date_end + ' 23:59:59'
            date_start = datetime.strptime(date_start, '%Y/%m/%d %H:%M:%S') + timedelta(hours=abs(time_zone))
            date_end = datetime.strptime(date_end, '%Y/%m/%d %H:%M:%S') + timedelta(hours=abs(time_zone))
            for pos_config_row in self.pos_config_ids:
                order_rows = self.env['pos.order'].search([('config_id','=', pos_config_row.id), ('date_order','>=', date_start),('date_order','<=', date_end), ('state','=', 'done'),('pos_global','=', False)])
                cash_count = bank_count = 0
                for order_row in order_rows:
                    if order_row.amount_total <= 0.0:
                        continue
                    bank = False
                    for payment_row in  order_row.payment_ids:
                        bank = False
                        if not payment_row.payment_method_id.is_cash_count:
                            bank = True
                            break
                    if bank:
                        bank_count += 1
                        if order_row._fields.get('amount_total_with_return',False):
                            amount += order_row.amount_total_with_return
                        else:
                            if order_row.amount_total <= 0.0:
                                continue
                            amount += order_row.amount_total
                    else:
                        cash_count += 1
                        if order_row._fields.get('amount_total_with_return',False):
                            amount_cash += order_row.amount_total_with_return
                        else:
                            amount_cash += order_row.amount_total
            self.payment_bank = amount
            self.payment_cash = amount_cash
            if self.type_inv == 'cash':
                self.amount = amount_cash
            elif self.type_inv == 'bank':
                self.amount = amount
            else:
                self.amount = amount + amount_cash
            # self.amount = amount + amount_cash
        else:
            self.payment_bank = 0.0
            self.payment_cash = 0.0

        return {
            'name':("Facturacion Global"),
            'view_mode': 'form',
            'view_id': False,
            'view_type': 'form',
            'res_model': 'invoice.global.wizard',
            'res_id': self.id,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }


    @api.onchange('pos_config_ids')
    def _onchange_pos_config_id(self):
        amount = 0.0
        amount_cash = 0.0
        if not self.journal_id and self.pos_config_ids:
            self.journal_id = self.pos_config_ids[0].journal_id
        if not self.pos_config_ids:
            self.journal_id = False
        return {}

    @api.onchange('date_start')
    def _onchange_date_start(self):
        self.date_end = self.date_start
        return {}

    @api.onchange('type_inv')
    def _onchange_type_inv(self):
        if self.type_inv == 'cash':
            self.amount = self.payment_cash
        elif self.type_inv == 'bank':
            self.amount = self.payment_bank
        else:
            self.amount = self.payment_cash + self.payment_bank
        return {}

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
        if self.type_inv in ('bank', 'cash_bank'):
            if self.sale_inv == 'product':
                # Cremamosreamos Factura Global
                move_vals,pos_order_rows = self._prepare_invoice_vals(inv_type_payment='Banco', pos_add_in_invoice=pos_order_used_rows)
                pos_order_used_rows |= pos_order_rows
            else:
                # Cremamosreamos Factura Global
                move_vals,pos_order_rows = self._prepare_invoice_by_sale_vals(inv_type_payment='Banco', pos_add_in_invoice=pos_order_used_rows)
                pos_order_used_rows |= pos_order_rows
            if move_vals:
                new_move = self.env['account.move'].sudo().with_company(self.journal_id.company_id).with_context(default_move_type='out_invoice').create(move_vals)
                new_moves_rows |= new_move
                message = _("This invoice has been created from the POS: %s") % (pos_links,)
                new_move.message_post(body=message)
                # self.pos_order_ids.write({'account_move_global': new_move.id, 'pos_global': True, 'state': 'invoiced'})           
                # self.pos_order_ids.write({'account_move': new_move.id, 'state': 'invoiced', 'pos_global': True, 'partner_id': self.partner_id.id})
                pos_order_rows.write({'account_move': new_move.id,'account_move_global': new_move.id, 'pos_global': True, 'state': 'invoiced','partner_id': self.partner_id.id})
                new_move.sudo().with_company(self.journal_id.company_id).action_post()
        if not pos_order_used_rows:
            pos_order_used_rows = self.env['pos.order']
        if self.type_inv in ('cash', 'cash_bank'):
            # Creamos Factura Global
            if self.sale_inv == 'product':
                move_cash_vals,pos_order_rows = self._prepare_invoice_vals(inv_type_payment='Efectivo', pos_add_in_invoice=pos_order_used_rows)
            else:
                # Cremamosreamos Factura Global
                move_cash_vals,pos_order_rows = self._prepare_invoice_by_sale_vals(inv_type_payment='Efectivo', pos_add_in_invoice=pos_order_used_rows)
            if move_cash_vals:
                new_move_cash = self.env['account.move'].sudo().with_company(self.journal_id.company_id).with_context(default_move_type='out_invoice').create(move_cash_vals)
                new_moves_rows |= new_move_cash
                message = _("This invoice has been created from the POS: %s") % (pos_links,)
                new_move_cash.message_post(body=message)
                # self.pos_order_ids.write({'account_move_global': new_move.id, 'pos_global': True})
                pos_order_rows.write({'account_move': new_move_cash.id,'account_move_global': new_move_cash.id, 'pos_global': True, 'state': 'invoiced','partner_id': self.partner_id.id})
                new_move_cash.sudo().with_company(self.journal_id.company_id).action_post()
        #########################################################################
        ## Se pidio solo crear la factura y aplicarle su reversal
        ########################################################################
        # #Cancelamos los movimientos de las ventas que see crearon al cerrar sesion
        # for order_row in self.pos_order_ids:
        #     session_rows |= order_row.session_id
        # # Eliminamos movimiento de sesion y cerramos denuevo para aplicar el pago a ala factura
        # for session_row in session_rows:
        #     session_row.statement_ids.button_reopen()
        #     move_line_rows = self.env['account.move']
        #     for statement_row in session_row.statement_ids:
        #         statement_row.line_ids.unlink()
        #     session_row.move_id.line_ids.remove_move_reconcile()
        #     session_row.move_id.button_draft()
        #     session_row.move_id.button_cancel()
        #     session_row.move_id.with_context(force_delete=True).unlink()
        #     session_row.write({'move_id': False, 'state':'closing_control'})
        #     session_row.order_ids.filtered(lambda order: order.state == 'done').write({'state':'paid', 'account_move': False})
        #     session_row.action_pos_session_validate()
        ###########################################################################
        # Reversa de Factura en Banco
        if new_move:
            reversal_row = self.env['account.move.reversal'].create({'move_ids': [(6,0,new_move.ids)], 'refund_method': 'cancel'})
            reversal_row.reverse_moves()
            new_move.move_type = 'out_invoice'
        # Reversa de Factura en Efectivo
        if new_move_cash:
            reversal_row = self.env['account.move.reversal'].create({'move_ids': [(6,0,new_move_cash.ids)], 'refund_method': 'cancel'})
            reversal_row.reverse_moves()
            new_move_cash.move_type = 'out_invoice'
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

    def action_calculate(self):
        self.ensure_one()
        if self.amount <= 0.0:
            raise UserError(_("Calcule el monto posible para facturar. Presione el boton obtener montos."))
        if self.type_inv == 'cash_bank':
            if self.payment_bank > self.amount:
                raise UserError(_("No se puede facturar un monto menor al cobrado en banco."))
        elif self.type_inv == 'cash':
            if self.payment_cash < self.amount:
                raise UserError(_("No se puede facturar un monto mayor al cobrado en Efectivo."))
        elif self.type_inv == 'bank':
            if self.payment_bank < self.amount:
                raise UserError(_("No se puede facturar un monto mayor al cobrado en Banco."))

        # Obtenemos el inicio y fin con hora y zona horaria del usuario
        time_zone = self._get_time_zone()
        # Obtenemos la fecha con 00:00 y 23:59
        date_start = self.date_start.strftime("%Y/%m/%d")
        date_end = self.date_end.strftime("%Y/%m/%d")
        date_start = date_start + ' 00:00:00'
        date_end = date_end + ' 23:59:59'
        date_start = datetime.strptime(date_start, '%Y/%m/%d %H:%M:%S') + timedelta(hours=abs(time_zone))
        date_end = datetime.strptime(date_end, '%Y/%m/%d %H:%M:%S') + timedelta(hours=abs(time_zone))
        wiz_order_rows = self.env['pos.order']
        amount = 0.0
        
        order_rows = self.env['pos.order'].search([('config_id','in', self.pos_config_ids.ids), ('date_order','>=', date_start),('date_order','<=',date_end), ('state','=', 'done'), ('pos_global','=', False)])
        if self.type_inv == 'cash_bank':
            # Se obtienen las bentas que se pagaran con metodos de pago que no son de efectivo
            for order_row in order_rows:
                added_order = False
                if order_row.id not in wiz_order_rows.ids and order_row.amount_total > 0.0:
                    for payment_row in  order_row.payment_ids:
                        if not payment_row.payment_method_id.is_cash_count:
                            if order_row._fields.get('amount_total_with_return',False):
                                if order_row.amount_total_with_return <= 0.0:
                                    continue
                                amount += order_row.amount_total_with_return
                                added_order = True
                            else:
                                amount += order_row.amount_total
                                added_order = True
                            if added_order:
                                wiz_order_rows |= order_row
                            break
            # Si aun queda monto por cubrir se obtienen ventas con pagos de tipo efectivo
            if round(amount,2) < self.amount:
                order_rows = self.env['pos.order'].search([('config_id','in', self.pos_config_ids.ids), ('date_order','>=', date_start),('date_order','<=', date_end), ('state','=', 'done'), ('pos_global','=', False),('id','not in',wiz_order_rows.ids)])
                for order_row in sorted( order_rows, key=lambda l: l.amount_total, reverse=False):
                    added_order = False
                    if order_row.id not in wiz_order_rows.ids and order_row.amount_total > 0.0:
                        if order_row._fields.get('amount_total_with_return',False):
                            if order_row.amount_total_with_return <= 0.0:
                                continue
                            amount += order_row.amount_total_with_return
                            added_order = True
                        else:
                            amount += order_row.amount_total
                            added_order = True
                        if added_order:
                            wiz_order_rows |= order_row
                        if amount >= self.amount:
                            break
        elif self.type_inv == 'cash':
            for order_row in sorted( order_rows, key=lambda l: l.amount_total, reverse=False):
                    added_order = False
                    if order_row.id not in wiz_order_rows.ids and order_row.amount_total > 0.0:
                        for payment_row in  order_row.payment_ids:
                            if payment_row.payment_method_id.is_cash_count:
                                if order_row._fields.get('amount_total_with_return',False):
                                    if order_row.amount_total_with_return <= 0.0:
                                        continue
                                    amount += order_row.amount_total_with_return
                                    added_order = True
                                else:
                                    amount += order_row.amount_total
                                    added_order = True
                                if added_order:
                                    wiz_order_rows |= order_row
                                break
                        if round(amount,2) >= self.amount:
                            break
        elif self.type_inv == 'bank':
            for order_row in sorted( order_rows, key=lambda l: l.amount_total, reverse=False):
                    added_order = False
                    if order_row.id not in wiz_order_rows.ids and order_row.amount_total > 0.0:
                        for payment_row in  order_row.payment_ids:
                            if not payment_row.payment_method_id.is_cash_count:
                                if order_row._fields.get('amount_total_with_return',False):
                                    if order_row.amount_total_with_return <= 0.0:
                                        continue
                                    amount += order_row.amount_total_with_return
                                    added_order = True
                                else:
                                    amount += order_row.amount_total
                                    added_order = True
                                if added_order:
                                    wiz_order_rows |= order_row
                                break
                        if round(amount,2) >= self.amount:
                            break


        if wiz_order_rows:
            self.pos_order_ids = wiz_order_rows
        return {
            'name':("Facturacion Global"),
            'view_mode': 'form',
            'view_id': False,
            'view_type': 'form',
            'res_model': 'invoice.global.wizard',
            'res_id': self.id,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

    def _prepare_invoice_data(self, inv_type_payment='Banco'):
        vals = {}
        # Obtenemos el inicio y fin con hora y zona horaria del usuario
        time_zone = self._get_time_zone()
        # Obtenemos la fecha con 00:00 y 23:59
        date_start = self.date_start.strftime("%Y/%m/%d")
        date_end = self.date_end.strftime("%Y/%m/%d")
        date_start = date_start + ' 00:00:00'
        date_end = date_end + ' 23:59:59'
        date_start = datetime.strptime(date_start, '%Y/%m/%d %H:%M:%S') + timedelta(hours=abs(time_zone))
        date_end = datetime.strptime(date_end, '%Y/%m/%d %H:%M:%S') + timedelta(hours=abs(time_zone))
        order_line_rows = self.env['pos.order.line']
        # for order_row in self.pos_order_ids:
        #     order_line_rows |= order_row.lines
        pos_name = "TPV"
        if len(self.pos_config_ids) == 1:
            pos_name = self.pos_config_ids.name
        name = "FG %s %s : %s - %s"%(inv_type_payment,pos_name, date_start.date(), date_end.date())
        fiscal_position_id = self.env['account.fiscal.position'].get_fiscal_position(self.partner_id.id).id
        vals = {
            'payment_reference': name,
            'invoice_origin': name,
            'journal_id': self.journal_id.id,
            'move_type': 'out_invoice',
            'ref': name,
            'partner_id': self.partner_id.id,
            'pos_global': True,
            # considering partner's sale pricelist's currency
            'currency_id': self.journal_id.currency_id and self.journal_id.currency_id.id or self.journal_id.company_id.currency_id.id,
            'invoice_user_id': self.env.user.id,
            'invoice_date': fields.Datetime.now(),
            'fiscal_position_id': fiscal_position_id or False,
            'invoice_line_ids': [],
            # 'invoice_cash_rounding_id': self.pos_config_id.rounding_method.id if self.pos_config_id.cash_rounding else False
        }
        return vals

    def _compute_order_taxes_by_tax(self, order):
        ''' 
        Metodo para obtener monto de impuestos agrupados por impuesto
        '''
        tax_group = {}
        fpos = order.fiscal_position_id
        for line in order.lines:
            if line._fields.get('qty_return',False):
                qty = line.qty - line.qty_return
            else:
                qty = line.qty
            if qty <= 0:
                continue
            if line.tax_ids:
                tax_ids_after_fiscal_position = fpos.map_tax(line.tax_ids, line.product_id, order.partner_id)
                price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
                taxes_vals = tax_ids_after_fiscal_position.compute_all(price, order.pricelist_id.currency_id, line.qty, product=line.product_id, partner=order.partner_id)
                taxes = taxes_vals['taxes']
                for line_tax in taxes:
                    if line_tax.get('price_include'):
                        price_unit = line_tax.get('base') + line_tax.get('amount')
                    else:
                        price_unit = line_tax.get('base')
                    if tax_group.get(line_tax.get('id')):
                        tax_group.get(line_tax.get('id')).update({'base': tax_group.get(line_tax.get('id')).get('base') + line_tax.get('base'), 'amount': tax_group.get(line_tax.get('id')).get('amount') + line_tax.get('amount'), 'price_unit': tax_group.get(line_tax.get('id')).get('price_unit') + price_unit})
                    else:
                        tax_group.update({line_tax.get('id'): {'base': line_tax.get('base'), 'amount': line_tax.get('amount'),'price_unit': price_unit}})
            else:
                price = line.price_subtotal
                if tax_group.get('without_tax'):
                    tax_group.get('without_tax').update({'base': tax_group.get('without_tax').get('base') + price, 'price_unit': tax_group.get('without_tax').get('price_unit') + price})
                else:
                    tax_group.update({'without_tax': {'base': price, 'amount': 0.0, 'price_unit': price}})
        return tax_group

    def _prepare_invoice_by_sale_vals(self, inv_type_payment='Banco', pos_add_in_invoice = []):
        self.ensure_one()
        if not pos_add_in_invoice:
            pos_add_in_invoice = self.env['pos.order']
        # Obtenemos datos de la venta generales
        vals = self._prepare_invoice_data(inv_type_payment)
        invoice_line_ids = []
        pos_order_rows = self.env['pos.order']        
        for order_row in self.pos_order_ids:
            if order_row in pos_add_in_invoice:
                continue
            for payment_row in order_row.payment_ids:
                if not payment_row.payment_method_id.is_cash_count and inv_type_payment=='Banco':
                    # Obtenemos los montos por impuesto de la venta
                    tax_group = self._compute_order_taxes_by_tax(order_row)
                    invoice_line_ids.extend(self._prepare_invoice_line_by_order(tax_group, order_row))
                    pos_order_rows += order_row
                    break
                elif payment_row.payment_method_id.is_cash_count and inv_type_payment=='Efectivo':  
                    # Obtenemos los montos por impuesto de la venta
                    tax_group = self._compute_order_taxes_by_tax(order_row)
                    invoice_line_ids.extend(self._prepare_invoice_line_by_order(tax_group,order_row))
                    pos_order_rows += order_row
                    break
        if not invoice_line_ids:
            return False,False
        vals.update({'invoice_line_ids': invoice_line_ids})
        return vals, pos_order_rows

    def _prepare_invoice_line_by_order(self, tax_group, order):
        line_ids = []
        # Obtenemos moneda del diario de la factura Global
        currency = self.journal_id.currency_id and self.journal_id.currency_id or self.journal_id.company_id.currency_id
        product_row = self.env['product.template'].search([('type', '=', 'product')], limit=1)
        accounts = product_row.get_product_accounts()
        for tax_id in tax_group.keys():
            price_unit = round(tax_group.get(tax_id).get('price_unit'),2)
            if tax_id == 'without_tax':
                if currency != order.currency_id:
                    price_unit = order.currency_id._convert(price_unit, currency, self.journal_id.company_id)
                line_vals = {
                    'product_id': False,
                    'quantity': 1,
                    'discount': 0,
                    'price_unit': price_unit,
                    'name': order.name,
                    'tax_ids': [(6, 0, [])],
                    'product_uom_id': self.uom_id.id,
                    'account_id': accounts['income'].id,
                }
                line_ids.append((0, None, line_vals))
                
            else:
                if currency != order.currency_id:
                    base = order.currency_id._convert(base, currency, self.journal_id.company_id)
                line_vals = {
                    'product_id': False,
                    'quantity': 1,
                    'discount': 0,
                    'price_unit': price_unit,
                    'name': order.name,
                    'tax_ids': [(6, 0, [tax_id])],
                    'product_uom_id': self.uom_id.id,
                    'account_id': accounts['income'].id,
                }
                line_ids.append((0, None, line_vals))
        return line_ids

    def _prepare_invoice_vals(self, inv_type_payment='Banco', pos_add_in_invoice = []):        
        self.ensure_one()
        # Obtenemos datos de la venta generales
        vals = self._prepare_invoice_data(inv_type_payment)
        invoice_line_ids = []
        pos_order_rows = self.env['pos.order']
        for order_row in self.pos_order_ids:
            if order_row in pos_add_in_invoice:
                continue
            for payment_row in order_row.payment_ids:
                if not payment_row.payment_method_id.is_cash_count and inv_type_payment=='Banco':
                    for line in order_row.lines:
                        if line._fields.get('qty_return',False):
                            qty = line.qty - line.qty_return
                        else:
                            qty = line.qty
                        if qty <= 0:
                            continue
                        if line.price_subtotal > 0:
                            invoice_line_ids.append((0, None, self._prepare_invoice_line(line)))
                            pos_order_rows += order_row
                    break
                elif payment_row.payment_method_id.is_cash_count and inv_type_payment=='Efectivo':  
                    for line in order_row.lines:
                        if line._fields.get('qty_return',False):
                            qty = line.qty - line.qty_return
                        else:
                            qty = line.qty
                        if qty <= 0:
                            continue
                        if line.price_subtotal > 0:
                            invoice_line_ids.append((0, None, self._prepare_invoice_line(line)))
                            pos_order_rows += order_row
                    break
        if not invoice_line_ids:
            return False,False     
        vals.update({'invoice_line_ids': invoice_line_ids})  
        return vals,pos_order_rows

    def _prepare_invoice_line(self, order_line):
        if order_line._fields.get('qty_return',False):
            qty = order_line.qty - order_line.qty_return
        else:
            qty = order_line.qty
        currency = self.journal_id.currency_id and self.journal_id.currency_id or self.journal_id.company_id.currency_id
        if currency != order_line.order_id.currency_id:
            price_unit = order_line.order_id.currency_id._convert(order_line.price_unit, currency, self.journal_id.company_id)
        else:
            price_unit = order_line.price_unit

        return {
            'product_id': order_line.product_id.id,
            'quantity': qty,
            'discount': order_line.discount,
            'price_unit': price_unit,
            'name': order_line.product_id.display_name,
            'tax_ids': [(6, 0, order_line.tax_ids_after_fiscal_position.ids)],
            'product_uom_id': order_line.product_uom_id.id,
        }