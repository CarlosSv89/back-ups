# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class tema_gas_red(models.Model):
#     _name = 'tema_gas_red.tema_gas_red'
#     _description = 'tema_gas_red.tema_gas_red'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
