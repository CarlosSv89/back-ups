# -*- coding: utf-8 -*-
{
    'name': "Validación de órdenes de venta",

    'summary': """""",

    'description': """
    """,

    'author': "Onasis Alcaraz",
    'website': "",

    'category': 'Sales/Point of Sale',
    'version': '0.1',

    'depends': ['base','point_of_sale', 'account','pos_route_config'],

    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/validacion.xml',
        'views/filtro_ventas.xml',
        'data/pos_order_data.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
}