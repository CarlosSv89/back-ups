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

class AccountMove(models.Model):
    _inherit = "account.move"

    date_time_sign_inv = fields.Datetime(
        string="Fecha para timbrar factura global", readonly=True, copy=False,
        help="Aqui se almacena la fecha en que se quiere timbrar la factura")

    def _post(self, soft=True):
        res = super(AccountMove, self)._post(soft=soft)
        for move in self:
            if move.pos_global and move.date_time_sign_inv:
                if move.l10n_mx_edi_post_time < move.date_time_sign_inv:
                    move.l10n_mx_edi_post_time = move.date_time_sign_inv
        return res