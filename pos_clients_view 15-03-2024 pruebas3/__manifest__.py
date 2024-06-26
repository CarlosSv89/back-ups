# -*- coding: utf-8 -*-
{
    'name': "pos_clients_view",

    'summary': """
        Modulo para editar punto de venta""",

    'description': """
        Modulo para la edicion de punto de venta
    """,

    'author': "Grupo Tomza",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'point_of_sale'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # qweb templates for the pos
    'qweb': ['static/src/xml/pos_clients_view.xml'],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
