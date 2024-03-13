# -*- coding: utf-8 -*-

from odoo import models, fields, api


class clase_cliente(models.Model):
    _inherit = 'res.partner'
    
    # ----------------- Fields to set tracking property -----------------
    char_tracking = ['name', 'function', 'street_name', 'street_number', 'street_number2', 'city', 'zip', 'vat', 'l10n_mx_edi_operator_licence', 
                    'x_studio_cruce', 'mobile', 'website', 'x_studio_region', 'barcode', 'ref', 'id_cliente_gaspar', 'id_cliente', 'modelo_medidor',
                    'departamento', 'torre', 'medidor_serie', 'edificio_sm', 'cta', 'clabe', 'convenio_cie']
    selection_tracking = ['company_type', 'lang', 'unidad_medida', 'banco', 'regimen']
    many2one_tracking = ['parent_id', 'title', 'city_id', 'state_id', 'property_payment_term_id', 'property_supplier_payment_term_id', 
                        'property_payment_method_id', 'property_product_pricelist', 'property_purchase_currency_id', 'property_account_position_id', 
                        'company_id', 'industry_id', 'property_stock_customer', 'property_stock_supplier', 'property_account_receivable_id', 
                        'property_account_payable_id', 'l10n_mx_edi_addenda', 'conciciones_pago_id']
    float_tracking = ['credit_limit', 'discount', 'loyalty_points', 'partner_latitude', 'partner_longitude', 'troya_factor_10k', 'troya_factor_20k',
                    'troya_factor_30k', 'troya_factor_45k', 'troya_convenio_10k', 'troya_convenio_20k', 'troya_convenio_30k', 'troya_convenio_45k',
                    'lectura_actual','factor_medidor','factor_conversion']
    boolean_tracking = ['is_comisionista_cliente', 'receipt_reminder_email', 'x_studio_gas_vehicular', 'l10n_mx_edi_no_tax_breakdown', 'convenio_troya',
                        'servicio_medido', 'bloqueo']
    
    # Set tracking for Char fields
    for field in char_tracking:
        vars()[field] = fields.Char(tracking=True)

    # Set tracking for Selection fields
    for field in selection_tracking:
        vars()[field] = fields.Selection(tracking=True)
    
    # Set Tracking for Many2one fields
    for field in many2one_tracking:
        vars()[field] = fields.Many2one(tracking=True)
    
    # Set tracking for Float fields 
    for field in float_tracking:
        vars()[field] = fields.Float(tracking=True)
        
    # Set tracking for Boolean fields
    for field in boolean_tracking:
        vars()[field] = fields.Boolean(tracking=True)
    
    
    reminder_date_before_receipt = fields.Integer(tracking=True)
    scheme = fields.Integer(tracking=True)
    radio = fields.Integer(tracking=True)
    capacity = fields.Integer(tracking=True)
    referencia_interna = fields.Integer(tracking=True)
    num_candado = fields.Integer(tracking=True)
    dias = fields.Integer(tracking=True)
    referencia_cie = fields.Integer(tracking=True)
    
    comment = fields.Text(tracking=True)

    
    child_ids = fields.One2many(tracking=True)
    bank_ids = fields.One2many(tracking=True)
    
    date_localization = fields.Date(tracking=True)
    fecha_periodo = fields.Date(tracking=True)
    
    # ----------------- Selection Fields tracking -----------------
    x_studio_estado_contrato = fields.Selection(tracking=True, selection=[('VIGENTE', 'VIGENTE'), ('SUSPENDIDO', 'SUSPENDIDO')])
    x_studio_estatus = fields.Selection(tracking=True, selection=[('ACTIVO', 'ACTIVO'), ('BAJA', 'BAJA')])
    x_studio_sub_canal_com = fields.Selection(tracking=True, selection=[('Autotanque', 'Autotanque'), ('Portátil', 'Portátil'), ('Carburación', 'Carburación'), ('Venta Casa', 'Venta Casa'), ('TRAS', 'TRAS')])
    x_studio_giro_comercial = fields.Selection(tracking=True, selection=[('Industrial', 'Industrial'), ('Comercial', 'Comercial'), ('Domestico', 'Domestico'), ('Gubernamental', 'Gubernamental'), ('Administradoras', 'Administradoras'), ('Estaciones de carburacion', 'Estaciones de carburacion')])
    x_studio_empresa_asociada = fields.Selection(tracking=True, selection=[('No aplica', 'No aplica'), ('Nuevo Casas Grndes', 'Nuevo Casas Grandes')])
    l10n_mx_type_of_operation = fields.Selection(tracking=True, selection=[('03', '03 - Prestacion de servicios profesionales'),('06', '06 - Alquiler de edificios'),('85', '85 - Otros')])
    tipo_descuento = fields.Selection(tracking=True, selection=[('cash', 'Efectivo'),('porcentage', 'Porcentaje')])
    l10n_mx_edi_fiscal_regime = fields.Selection(tracking=True, selection=[('601', '601 - General de Ley Personas Morales'),('603', '603 - Personas Morales con Fines no Lucrativos'),('605', '605 - Sueldos y Salarios e Ingresos Asimilados a Salarios'),('606', '606 - Arrendamiento'),('607', '607 - Régimen de Enajenación o Adquisición de Bienes'),('608', '608 - Demás ingresos'),('609', '609 - Consolidación'),('610', '610 - Residentes en el Extranjero sin Establecimiento Permanente en México'),('611', '611 - Ingresos por Dividendos (socios y accionistas)'),('612', '612 - Personas Físicas con Actividades Empresariales y Profesionales'),('614', '614 - Ingresos por intereses'),('615','615 - Régimen de los ingresos por obtención de premios'),('616', '616 - Sin obligaciones fiscales'),('620', '620 - Sociedades Cooperativas de Producción que optan por diferir sus ingresos'),('621', '621 - Incorporación Fiscal'),('622', '622 - Actividades Agrícolas, Ganaderas, Silvícolas y Pesqueras'),('623', '623 - Opcional para Grupos de Sociedades'),('624', '624 - Coordinados'),('625', '625 - Régimen de las Actividades Empresariales con ingresos a través de Plataformas Tecnológicas'),('626', '626 - Régimen Simplificado de Confianza - RESICO'),('628', '628 - Hidrocarburos'),('629', '629 - De los Regímenes Fiscales Preferentes y de las Empresas Multinacionales'),('630', '630 - Enajenación de acciones en bolsa de valores')])
    
    # -------------------------------------------------------------------------
    
    # Tracking = true all fields
    # @api.model
    # def _add_tracking_to_fields(self):
    #     for field in self._fields.values():
    #         field.tracking = True
    
    # @api.model
    # def init(self):
    #     super(clase_cliente, self).init()
    #     self._add_tracking_to_fields()
    
    
    clase = fields.Selection(string='Clase', tracking=True,
    selection=[('revolvente', 'REVOLVENTE'), ('juridico', 'JURIDICO'), ('incobrable', 'INCOBRABLE'), ('inactivo', 'INACTIVO')])

