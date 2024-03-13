from odoo import models


class DiarioSaldosPorCobrarReport(models.Model):
    _name = 'report.rep.diario.saldos.xcobrar.report'
    _description = 'reporte de saldos por cobrar excel'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, diarios):
        for diario in diarios:

            black_text_cell = workbook.add_format({'bold': True, 'font_color': 'black', 'bg_color': 'white','border': True, 'border_color': '#538dd5'})
            black_number_cell = workbook.add_format({'bold': True, 'font_color': 'black', 'bg_color': 'white','border': True, 'border_color': '#538dd5', 'num_format': '#,##0.00'})
            black_percent_cell = workbook.add_format({'bold': True, 'font_color': 'black', 'bg_color': 'white','border': True, 'border_color': '#538dd5', 'num_format': '%#,##0.00'})
            red_number_cell = workbook.add_format({'bold': True, 'font_color': 'b80f0a', 'bg_color': 'white','border': True, 'border_color': '#538dd5', 'num_format': '#,##0.00'})

            tuscany_format = workbook.add_format({'bold': True, 'font_color': 'black', 'bg_color': 'fcd12a','border': True, 'border_color': '#538dd5', 'align': 'center'})
            navy_cell = workbook.add_format({'bold': True, 'font_color': 'white', 'bg_color': '000080','border': True, 'border_color': '#538dd5'})
            azure_cell = workbook.add_format({'bold': True, 'font_color': 'white', 'bg_color': '0080FF','border': True, 'border_color': '#538dd5'})

            crimson_text_cell = workbook.add_format({'bold': True, 'font_color': 'white', 'bg_color': 'b80f0a','border': True, 'border_color': '#538dd5'})
            crimson_number_cell = workbook.add_format({'bold': True, 'font_color': 'white', 'bg_color': 'b80f0a','border': True, 'border_color': '#538dd5', 'num_format': '#,##0.00'})


            sheet = workbook.add_worksheet('Saldos por cobrar')
            sheet.merge_range('A1:M1', diario.name, workbook.add_format({'bold': True}))

            sheet.merge_range('A2:M2', diario.company_name, workbook.add_format({'bold': True}))  

            sheet.merge_range('B4:M4', diario.fecha_inicial.year, tuscany_format)

            sheet.set_column(0, 0, 35)
            sheet.set_column(1, 12, 15)

            row = 4
            sheet.write(row, 0, 'CONCEPTO', azure_cell)
            sheet.write(row, 1, 'Enero', azure_cell)
            sheet.write(row, 2, 'Febrero', azure_cell)
            sheet.write(row, 3, 'Marzo', azure_cell)
            sheet.write(row, 4, 'Abril', azure_cell)
            sheet.write(row, 5, 'Mayo', azure_cell)
            sheet.write(row, 6, 'Junio', azure_cell)
            sheet.write(row, 7, 'Julio', azure_cell)
            sheet.write(row, 8, 'Agosto', azure_cell)
            sheet.write(row, 9, 'Septiembre', azure_cell)
            sheet.write(row, 10, 'Octubre', azure_cell)
            sheet.write(row, 11, 'Noviembre', azure_cell)
            sheet.write(row, 12, 'Diciembre', azure_cell)

            row = 5
            first_row = row + 1

            for line in diario.linea_diario_rpt:
                if row == 5:

                    sheet.write(row, 0, line.concepto, navy_cell)
                    sheet.write(row, 1, line.enero, black_number_cell)
                    sheet.write(row, 2, line.febrero, black_number_cell)
                    sheet.write(row, 3, line.marzo, black_number_cell)
                    sheet.write(row, 4, line.abril, black_number_cell)
                    sheet.write(row, 5, line.mayo, black_number_cell)
                    sheet.write(row, 6, line.junio, black_number_cell)
                    sheet.write(row, 7, line.julio, black_number_cell)
                    sheet.write(row, 8, line.agosto, black_number_cell)
                    sheet.write(row, 9, line.septiembre, black_number_cell)
                    sheet.write(row, 10, line.octubre, black_number_cell)
                    sheet.write(row, 11, line.noviembre, black_number_cell)
                    sheet.write(row, 12, line.diciembre, black_number_cell)

                elif row == 6 or row == 7:
                
                    sheet.write(row, 0, line.concepto, navy_cell)
                    sheet.write(row, 1, line.enero, red_number_cell)
                    sheet.write(row, 2, line.febrero, red_number_cell)
                    sheet.write(row, 3, line.marzo, red_number_cell)
                    sheet.write(row, 4, line.abril, red_number_cell)
                    sheet.write(row, 5, line.mayo, red_number_cell)
                    sheet.write(row, 6, line.junio, red_number_cell)
                    sheet.write(row, 7, line.julio, red_number_cell)
                    sheet.write(row, 8, line.agosto, red_number_cell)
                    sheet.write(row, 9, line.septiembre, red_number_cell)
                    sheet.write(row, 10, line.octubre, red_number_cell)
                    sheet.write(row, 11, line.noviembre, red_number_cell)
                    sheet.write(row, 12, line.diciembre, red_number_cell)

                else:
                    sheet.write(row, 0, line.concepto, black_text_cell)
                    sheet.write(row, 1, line.enero, black_number_cell)
                    sheet.write(row, 2, line.febrero, black_number_cell)
                    sheet.write(row, 3, line.marzo, black_number_cell)
                    sheet.write(row, 4, line.abril, black_number_cell)
                    sheet.write(row, 5, line.mayo, black_number_cell)
                    sheet.write(row, 6, line.junio, black_number_cell)
                    sheet.write(row, 7, line.julio, black_number_cell)
                    sheet.write(row, 8, line.agosto, black_number_cell)
                    sheet.write(row, 9, line.septiembre, black_number_cell)
                    sheet.write(row, 10, line.octubre, black_number_cell)
                    sheet.write(row, 11, line.noviembre, black_number_cell)
                    sheet.write(row, 12, line.diciembre, black_number_cell)

                row += 1

            
            # Write a conditional format over a range B9:M20.
            sheet.conditional_format('B9:M20', {'type': 'cell',
                                         'criteria': '!=',
                                         'value': 0,
                                         'format': red_number_cell})

            # Write another conditional format over the same range.
            sheet.conditional_format('B9:M20', {'type': 'cell',
                                         'criteria': '==',
                                         'value': 0,
                                         'format': black_number_cell})


            row = 20
            sheet.write(row, 0, 'Saldo por cobrar', crimson_text_cell)
            sheet.write(row, 1, '=SUM(B' + str(first_row) + ':B' + str(row)+ ')', crimson_number_cell)
            sheet.write(row, 2, '=SUM(C' + str(first_row) + ':C' + str(row)+ ')', crimson_number_cell)
            sheet.write(row, 3, '=SUM(D' + str(first_row) + ':D' + str(row)+ ')', crimson_number_cell)
            sheet.write(row, 4, '=SUM(E' + str(first_row) + ':E' + str(row)+ ')', crimson_number_cell)
            sheet.write(row, 5, '=SUM(F' + str(first_row) + ':F' + str(row)+ ')', crimson_number_cell)
            sheet.write(row, 6, '=SUM(G' + str(first_row) + ':G' + str(row)+ ')', crimson_number_cell)
            sheet.write(row, 7, '=SUM(H' + str(first_row) + ':H' + str(row)+ ')', crimson_number_cell)
            sheet.write(row, 8, '=SUM(I' + str(first_row) + ':I' + str(row)+ ')', crimson_number_cell)
            sheet.write(row, 9, '=SUM(J' + str(first_row) + ':J' + str(row)+ ')', crimson_number_cell)
            sheet.write(row, 10, '=SUM(K' + str(first_row) + ':K' + str(row)+ ')', crimson_number_cell)
            sheet.write(row, 11, '=SUM(L' + str(first_row) + ':L' + str(row)+ ')', crimson_number_cell)
            sheet.write(row, 12, '=SUM(M' + str(first_row) + ':M' + str(row)+ ')', crimson_number_cell)

            # SALDO ENTRE META POR 100 - EXAMPLE ENERO: (B21/B6) el *100 se agrega con el formato de celda
            row = 21
            sheet.write(row, 0, '% Saldo por cobrar/Vencimientos netos', black_text_cell)
            sheet.write(row, 1, '=SI.ERROR((B' + str(row) + '/B' + str(first_row) + '),0.00)', black_percent_cell)
            sheet.write(row, 2, '=SI.ERROR((C' + str(row)+ '/C' + str(first_row) + '),0.00)', black_percent_cell)
            sheet.write(row, 3, '=SI.ERROR((D' + str(row)+ '/D' + str(first_row) + '),0.00)', black_percent_cell)
            sheet.write(row, 4, '=SI.ERROR((E' + str(row)+ '/E' + str(first_row) + '),0.00)', black_percent_cell)
            sheet.write(row, 5, '=SI.ERROR((F' + str(row)+ '/F' + str(first_row) + '),0.00)', black_percent_cell)
            sheet.write(row, 6, '=SI.ERROR((G' + str(row)+ '/G' + str(first_row) + '),0.00)', black_percent_cell)
            sheet.write(row, 7, '=SI.ERROR((H' + str(row)+ '/H' + str(first_row) + '),0.00)', black_percent_cell)
            sheet.write(row, 8, '=SI.ERROR((I' + str(row)+ '/I' + str(first_row) + '),0.00)', black_percent_cell)
            sheet.write(row, 9, '=SI.ERROR((J' + str(row)+ '/J' + str(first_row) + '),0.00)', black_percent_cell)
            sheet.write(row, 10, '=SI.ERROR((K' + str(row)+ '/K' + str(first_row) + '),0.00)', black_percent_cell)
            sheet.write(row, 11, '=SI.ERROR((L' + str(row)+ '/L' + str(first_row) + '),0.00)', black_percent_cell)
            sheet.write(row, 12, '=SI.ERROR((M' + str(row)+ '/M' + str(first_row) + '),0.00)', black_percent_cell)

            # -------------------
            
            sheet = workbook.add_worksheet('Desglose de ordenes')

            sheet.write(0, 0, 'Desglose de ordenes', workbook.add_format({'bold': True}))


            sheet.write(3, 0, 'Mes', azure_cell)
            sheet.write(3, 1, 'Fecha', azure_cell)
            sheet.write(3, 2, 'Fecha de vencimiento', azure_cell)
            sheet.write(3, 3, 'Ref. nota', azure_cell)
            sheet.write(3, 4, 'Cliente', azure_cell)
            sheet.write(3, 5, 'Total', azure_cell)
            row = 4

            for line in diario.linea_desglose_ordenes:
                sheet.write(row, 0, line.concepto, black_text_cell)
                sheet.write(row, 1, line.date_order)
                sheet.write(row, 2, line.date_order_due)
                sheet.write(row, 3, line.order_folio)
                sheet.write(row, 4, line.partner_id.name)
                sheet.write(row, 5, line.amount_total)
                row += 1

            # -------------------

            sheet = workbook.add_worksheet('Desglose de facturas')

            sheet.write(0, 0, 'Desglose de facturas', workbook.add_format({'bold': True}))

            sheet.write(3, 0, 'Mes', azure_cell)
            sheet.write(3, 1, 'Numero', azure_cell)
            sheet.write(3, 2, 'Folio fiscal', azure_cell)
            sheet.write(3, 3, 'Nombre del cliente', azure_cell)
            sheet.write(3, 4, 'Fecha de la factura', azure_cell)
            sheet.write(3, 5, 'Fecha de vencimiento', azure_cell)
            sheet.write(3, 6, 'Total', azure_cell)
            sheet.write(3, 7, 'Importe pendiente', azure_cell)
            sheet.write(3, 8, 'Facturacion electronica', azure_cell)
            sheet.write(3, 9, 'Estado del pago', azure_cell)
            sheet.write(3, 10, 'Estado', azure_cell)
            row = 4

            for line in diario.linea_desglose_facturas:
                sheet.write(row, 0, line.concepto, black_text_cell)
                sheet.write(row, 1, line.name)
                sheet.write(row, 2, line.l10n_mx_edi_cfdi_uuid)
                sheet.write(row, 3, line.invoice_partner_display_name)
                sheet.write(row, 4, line.invoice_date)
                sheet.write(row, 5, line.invoice_date_due)
                sheet.write(row, 6, line.amount_total)
                sheet.write(row, 7, line.amount_residual_signed)
                sheet.write(row, 8, line.edi_state)
                sheet.write(row, 9, line.payment_state)
                sheet.write(row, 10, line.state)
                row += 1