# -*- coding: utf-8 -*-

from odoo import models, fields, api
# Testing new git pc

class catalogo(models.Model):
    _name = 'catalogo.variables'
    _description = 'Caracteristicas de variables'

    name = fields.Char(string='Nombre de variable', required=True)
    nivel = fields.Integer(string='Nivel', required=True)
    padre_id = fields.Integer(string='ID Padre', required=False)
    numero = fields.Integer(string='Numero', required=True)

    anno = fields.Char(string='Año', default='2024')
    # months = fields.One2many(comodel_name='catalogo.reportes', inverse_name='relacion_ids', string='meses')


class reporte(models.Model):
    _name = 'catalogo.reportes'
    _description = 'Caracteristicas de reportes'

    fecha_filtro = fields.Selection(string='Año', selection=[('2004','2004')], default='')

    enero = fields.Float('Enero', (5,1), default=0.0)
    febrero = fields.Float('Febrero', (5,1), default=0.0)
    marzo = fields.Float('Marzo', (5,1), default=0.0)
    

    relacion_ids = fields.One2many('catalogo.data', 'data_ids', string='Relacion')

    @api.onchange('fecha_filtro')
    def _get_name(self):
        for doc in self:
            if doc.fecha_filtro != '':
                rec = self.env['catalogo.variables'].search([])
                self.relacion_ids = [(5,0,0)]
                for res in rec:
                    line = {}
                    line['name'] = res.name
                    line['nivel'] = res.nivel
                    line['padre_id'] = res.padre_id
                    line['numero'] = res.numero
                    self.relacion_ids = [(0,0,line)]
            else:
                self.relacion_ids = [(0,0,line)]

class reporte_data(models.Model):
    _name='catalogo.data'
    _description='Clase para obtener variables'

    data_ids = fields.Many2one('catalogo.reportes', string='Variables', readonly=True)

    name = fields.Char(string='Nombre variable')
    nivel = fields.Integer(string='Nivel')
    padre_id = fields.Integer(string='Padre ID')
    numero = fields.Integer(string='Numero')