# -*- coding: utf-8 -*-
{
    'name': "G4S",

    'summary': """
        Agrega funcionalidad de gaspar""",

    'description': """
        Agrega funcionalidad de gaspar
    """,

    'author': "Grupo Tomza, Hipólito Rodríguez",
    'website': "https://www.gazready.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'contacts', 'base_address_city', 'pos_assets', 'descuentos', 'report_xlsx'],

    # always loaded
    'data': [
        'reports/report.xml',
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/condiciones_pago.xml',
        'views/gaspar_dist_center.xml',
        'views/gaspar_eventos_reporte.xml',
        'views/gaspar_precios.xml',
        'views/gaspar_medidor.xml',
        'views/gaspar_report.xml',
        'views/gaspar_ruta_reporte.xml',
        'views/gaspar_clientes.xml',
        'views/res_company.xml',
        'views/res_partner.xml',
        'views/ruta_cliente.xml',
        'views/settings.xml',
        'views/views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
