from odoo import models

class FacturasPueReport(models.Model):
  _name = 'report.rep_credito.facturas_pue.report'
  _inherit = 'report.report_xlsx.abstract'


  def generate_xlsx_report(self, workbook, data, facturas):
    for factura in facturas:
      # Establecer el nombre del reporte
      report_name = 'Reporte de Facturas PUE'

      # Titulo del reporte
      report_title = 'Reporte de Facturas PUE del ' + str(factura.fecha_inicial) + ' al ' + str(factura.fecha_final)

      # Establecer el nombre de la hoja de Excel
      sheet = workbook.add_worksheet(report_name[:31])
      sheet.write(0, 6, report_title, workbook.add_format({'bold': True, 'align': 'center', 'font_size': 16}))

      # Establecer el ancho de las columnas
      sheet.set_column(0, 0, 5)
      sheet.set_column(1, 1, 30)
      sheet.set_column(2, 2, 30)
      sheet.set_column(3, 3, 30)
      sheet.set_column(4, 4, 40)
      sheet.set_column(5, 5, 30)
      sheet.set_column(6, 6, 25)
      sheet.set_column(7, 7, 25)
      sheet.set_column(8, 8, 40)
      sheet.set_column(9, 9, 25)
      sheet.set_column(10, 10, 25)
      sheet.set_column(11, 11, 25)
      sheet.set_column(12, 12, 25)
      sheet.set_column(13, 13, 25)
      sheet.set_column(14, 14, 35)
      sheet.set_column(15, 15, 25)
      sheet.set_column(16, 16, 25)
      sheet.set_column(17, 17, 25)
      sheet.set_column(18, 18, 40)
      sheet.set_column(19, 19, 25)

      # Formato de celdas
      title_cell = workbook.add_format({'bold': True, 'font_color': '#ffff', 'border': True, 'border_color': '#ffff', 'bg_color': '#28a6c5', 'align': 'center'})
      normal_cell = workbook.add_format({'font_color': 'black', 'border': True, 'border_color': '#F1FADA', 'align': 'center'})
      id_cell = workbook.add_format({'num_format':'0,000','font_color': 'black', 'border': True, 'border_color': '#F1FADA', 'align': 'center'})
      date_cell = workbook.add_format({'num_format': 'dd/mm/yyyy', 'font_color': 'black', 'border': True, 'border_color': '#F1FADA', 'align': 'center'})
      
    
      
      # Encabezados de las columnas
      sheet.write(2, 2, 'Número', title_cell)
      sheet.write(2, 3, 'Folio fiscal', title_cell)
      sheet.write(2, 4, 'Cliente', title_cell)
      sheet.write(2, 5, 'Nombre de tipo', title_cell)
      sheet.write(2, 6, 'Política de pago', title_cell)
      sheet.write(2, 7, 'Canal de distribución', title_cell)
      sheet.write(2, 8, 'Nombre del cliente', title_cell)
      sheet.write(2, 9, 'Términos de pago', title_cell)
      sheet.write(2, 10, 'Fecha de factura', title_cell)
      sheet.write(2, 11, 'Fecha de vencimiento', title_cell)
      sheet.write(2, 12, 'Tipo', title_cell)
      sheet.write(2, 13, 'Empresa', title_cell)
      sheet.write(2, 14, 'Importe sin impuesto firmado', title_cell)
      sheet.write(2, 15, 'Importe total firmado', title_cell)
      sheet.write(2, 16, 'Estado', title_cell)
      sheet.write(2, 17, 'Estado de pago', title_cell)
      sheet.write(2, 18, 'Facturación electrónica', title_cell)
      sheet.write(2, 19, 'Identificación', title_cell)

      # Linea en la que empiezan lod registros
      row = 3
      for line in factura.facturas_ids:
        sheet.write(row, 2, line.name, normal_cell)

        # Condicion de politicas de pago
        if line.l10n_mx_edi_cfdi_uuid:
          sheet.write(row, 3, line.l10n_mx_edi_cfdi_uuid, normal_cell)
        else:
          sheet.write(row, 3, '', normal_cell)

        sheet.write(row, 4, line.x_studio_cliente, normal_cell)
        sheet.write(row, 5, line.type_name, normal_cell)
        sheet.write(row, 6, line.l10n_mx_edi_payment_policy, normal_cell)

        # Condicion de canal de distribucion
        if line.canal_distribucion:
          sheet.write(row, 7, line.canal_distribucion, normal_cell)
        else:
          sheet.write(row, 7, '', normal_cell)

        sheet.write(row, 8, line.invoice_partner_display_name, normal_cell)

        # Condicion de terminos de pago
        if line.invoice_payment_term_id:
          sheet.write(row, 9, line.invoice_payment_term_id, normal_cell)
        else:
          sheet.write(row, 9, '', normal_cell)

        sheet.write(row, 10, line.invoice_date, date_cell)
        sheet.write(row, 11, line.invoice_date_due, date_cell)
        sheet.write(row, 12, line.x_studio_tipo, normal_cell)
        sheet.write(row, 13, line.company_id.name, normal_cell)
        sheet.write(row, 14, line.amount_untaxed_signed, normal_cell)
        sheet.write(row, 15, line.amount_total_signed, normal_cell)

        # Condicion de estado de la factura
        if line.state == 'posted':
          sheet.write(row, 16, 'Publicado', normal_cell)
        else:
          sheet.write(row, 16, line.state, normal_cell)

        # Condicion de estado de pago
        if line.payment_state == 'paid':
          sheet.write(row, 17, 'Pagado', normal_cell)
        elif line.payment_state == 'not_paid':
          sheet.write(row, 17, 'No pagado', normal_cell)
        elif line.payment_state == 'in_payment':
          sheet.write(row, 17, 'Pagado, sin conciliar', normal_cell)
        elif line.payment_state == 'partial':
          sheet.write(row, 17, 'Pagado parcialmente', normal_cell)
        elif line.payment_state == 'reversed':
          sheet.write(row, 17, 'Revertido', normal_cell)
        else:
          sheet.write(row, 17, 'Sistema anterior de facturación', normal_cell)
        
        # Condicion de estado EDI
        if line.edi_state == 'sent':
          sheet.write(row, 18, 'Enviado', normal_cell)
        elif line.edi_state == 'to_cancel':
          sheet.write(row, 18, 'Por cancelar', normal_cell)
        else:
          sheet.write(row, 18, line.edi_state, normal_cell)
        
        sheet.write(row, 19, line.id_factura, id_cell)
        row += 1


