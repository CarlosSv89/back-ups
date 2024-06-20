# -*- coding: utf-8 -*-
{
    'name': "Libro de ingresos",

    'summary': """
        Libro de ingresos""",

    'description': """
        Libro de ingresos
    """,

    'author': "Eduardo Rivas",
    'website': "http://www.ZAE.mx",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','report_xlsx'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/views.xml',
        'views/templates.xml',
        'reports/rpt_li.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
