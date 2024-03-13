# -*- coding: utf-8 -*-
{
    'name': "Reportes de crédito",

    'summary': """
        Reportes de crédito""",

    'description': """
        Reportes de crédito
    """,

    'author': "Hipólito Rodríguez Alvatado",
    'website': "http://www.gazready.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'report_xlsx', 'account'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'reports/diario_antiguedad_saldos_report.xml',
        'reports/diario_credito_cobranza_report.xml',
        'reports/diario_cliente_credito_cobranza_report.xml',
        'reports/diario_saldos_por_cobrar_report.xml',
        'views/views.xml',
        'views/diario_antiguedad_saldos.xml',
        'views/diario_cliente.xml',
        'views/diario_saldos_por_cobrar.xml',
        'views/facturas_pue.xml',
        'views/menu.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
