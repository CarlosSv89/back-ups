# -*- coding: utf-8 -*-
{
    'name': "endpoints_zae",

    'summary': """
        Endpoints ZAE""",

    'description': """
        Modulo para intentar llevar datos a ZAE ejecutivo
    """,

    'author': "Carlos Sánchez",
    'website': "http://www.zae.mx",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '1.0.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    # 'demo': [
    #     'demo/demo.xml',
    # ],
}
