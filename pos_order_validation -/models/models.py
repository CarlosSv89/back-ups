# -*- coding: utf-8 -*-

from logging.config import valid_ident
from wsgiref import validate
from odoo.exceptions import UserError
from odoo import models, fields, api
import warnings
from odoo import _

class posOrder_validation(models.Model):
    _inherit = 'pos.order'

    validation = fields.Char(string="Validación")
    validation_by = fields.Char(string="Validado por")

    def get_validate_by(self):
        orders = self.env['pos.order'].search([('validation', '=', None)])
        for order in orders:
            order.validation = 'Sin validar'
            order.validation_by = 'Sin validar'

    def validation_action(self):
        user_name = self.env.user.display_name
        for order in self:
            if order.validation =='Validado':
                raise UserError("Esta órden ya está validada")
            if order.validation == 'Sin validar':                 
                order.validation = 'Validado'
                order.validation_by = user_name

    def action_pos_order_invoice(self):
        if not self.validation =='Validado':
            raise UserError("Por favor valide la órden para poder facturar.")
        return super(posOrder_validation,self).action_pos_order_invoice()