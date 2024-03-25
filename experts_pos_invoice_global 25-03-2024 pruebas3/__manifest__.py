# -*- encoding: utf-8 -*-
##################################################################################################
#
#   Author: Experts SRL de CV (https://exdoo.mx)
#   Coded by: Carlos Blanco (carlos.blanco@exdoo.mx)
#   License: https://blog.exdoo.mx/licencia-de-uso-de-software/
#
##################################################################################################

{
    'name' : 'Factura Global del PoS',
    'version' : '1.0.0',
    'author' : 'www.exdoo.mx',
    'license': 'GPL-3',
    'category' : 'Point of Sale',
    'website' : 'https://exdoo.mx',
    'description': """
        Permite crear una factura con varias ventas PoS

        Si tiene dudas, quiere reportar algún error o mejora póngase en contacto con nosotros: info@exdoo.mx
    """,
    'data':[
        'security/ir.model.access.csv',
        'wizard/invoice_global_wizard_view.xml',
    ],
    'depends': ['base','point_of_sale','experts_groups'],
    'installable': True,
    'qweb': [
        ],
    'js': [
    ],

}
