# -*- encoding: utf-8 -*-
##################################################################################################
#
#   Author: Experts SRL de CV (https://exdoo.mx)
#   Coded by: Carlos Blanco (carlos.blanco@exdoo.mx)
#   License: https://blog.exdoo.mx/licencia-de-uso-de-software/
#
##################################################################################################

{
    'name': 'Mejoras para Tomza en factura Global',
    'version': '14.0',
    'depends': [
        'experts_pos_invoice_global','l10n_mx_edi'
    ],
    'author': 'Exdoo SA de CV',
    'category': 'stock',
    'website': 'https://exdoo.mx',
    'summary': 'Modulo que actualiza valores en picking',
    'description': '''
        Adecuaciones para Tomza en Factura global:
            - Se puede seleccionar la fecha de la factura global.
            - La facturación por venta tomara la unidad de medida de las líneas
            - La facturación por venta sumara todas las cantidades de las lineas de venta para ponerlo en la línea de factura, asi tambien se hace el caluclo del precio unitario.
    ''',
    'data': [
        "wizard/invoice_global_wizard_view.xml",
    ],
}