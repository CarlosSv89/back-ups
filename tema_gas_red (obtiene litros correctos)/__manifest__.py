# -*- coding: utf-8 -*-
{
    'name': "tema_gas_red",

    'summary': """
        tema_gas_red""",

    'description': """
        tema_gas_red
    """,

    'author': "Ema Terrones",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Themes/Backend',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','web', 'point_of_sale'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'qweb': [
        'static/src/xml/logo_menu.xml',
        'static/src/xml/listbox.xml',
        'static/src/xml/logo_pos.xml',

    ],
}
