# -*- coding: utf-8 -*-
{
    'name': "factura_pago_inmediato",

    'summary': """
        Factura de contado (Registro de pagos automáticos)""",

    'description': """
        Pagos automaticos para facturas de contado PUE
    """,

    'author': "Grupo Tomza",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/custom_wizard.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
