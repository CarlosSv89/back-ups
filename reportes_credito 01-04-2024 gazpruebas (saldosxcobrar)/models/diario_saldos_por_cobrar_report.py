from odoo import api, fields, models
import locale
from datetime import date
from dateutil.relativedelta import relativedelta
import logging
import string
_logger = logging.getLogger(__name__)

# Mes en español
locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')

class DiarioSaldosPorCobrarReport(models.Model):
    _name = 'report.rep.diario.saldos.xcobrar.report'
    _description = 'reporte de saldos por cobrar excel'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, diarios):
        # Dict to map letters to numbers
        letter_to_num = {letter: i for i, letter in enumerate(string.ascii_uppercase, start=1)}
        
        # Cells from B to AK
        col_range = [string.ascii_uppercase[i-1] for i in range(letter_to_num['B'], letter_to_num['Z'] + 1)]
        col_range += [f"A{string.ascii_uppercase[i-1]}" for i in range(letter_to_num['A'], letter_to_num['K'] + 1)]
            
        for diario in diarios:
            
            initial_month = diario.fecha_inicial.strftime("%B")
            final_month = diario.fecha_final.strftime("%B")

            black_text_cell = workbook.add_format({'bold': True, 'font_color': 'black', 'bg_color': 'white','border': True, 'border_color': '#538dd5'})
            black_number_cell = workbook.add_format({'bold': True, 'font_color': 'black', 'bg_color': 'white','border': True, 'border_color': '#538dd5', 'num_format': '#,##0.00'})
            black_percent_cell = workbook.add_format({'bold': True, 'font_color': 'black', 'bg_color': 'white','border': True, 'border_color': '#538dd5', 'num_format': '%#,##0.00'})
            red_number_cell = workbook.add_format({'bold': True, 'font_color': 'b80f0a', 'bg_color': 'white','border': True, 'border_color': '#538dd5', 'num_format': '#,##0.00'})

            tuscany_format = workbook.add_format({'bold': True, 'font_color': 'black', 'bg_color': 'fcd12a','border': True, 'border_color': '#538dd5', 'align': 'center'})
            navy_cell = workbook.add_format({'bold': True, 'font_color': 'white', 'bg_color': '000080','border': True, 'border_color': '#538dd5'})
            azure_cell = workbook.add_format({'bold': True, 'font_color': 'white', 'bg_color': '0080FF','border': True, 'border_color': '#538dd5'})

            crimson_text_cell = workbook.add_format({'bold': True, 'font_color': 'white', 'bg_color': 'b80f0a','border': True, 'border_color': '#538dd5'})
            crimson_number_cell = workbook.add_format({'bold': True, 'font_color': 'white', 'bg_color': 'b80f0a','border': True, 'border_color': '#538dd5', 'num_format': '#,##0.00'})

            
            # Getting number of filtered months
            def get_columns_number():
                start = diario.fecha_inicial
                end = diario.fecha_final
                
                months = (end.year - start.year) * 12 + end.month - start.month + 1
                return months

            sheet = workbook.add_worksheet('Saldos por cobrar')
            sheet.merge_range('A1:M1', diario.name, workbook.add_format({'bold': True}))

            sheet.merge_range('A2:M2', diario.company_name, workbook.add_format({'bold': True}))  

            sheet.merge_range(3,1,3,get_columns_number(), f"{initial_month.upper()} {diario.fecha_inicial.year} a {final_month.upper()} {diario.fecha_final.year}", tuscany_format)

            sheet.set_column(0, 0, 35)
            sheet.set_column(1, get_columns_number(), 15)
            
            

            row = 4
            
            # Dynamic titles
            date_alt = diario.fecha_inicial
            sheet.write(row, 0, 'CONCEPTO', azure_cell)
            for i in range(1,get_columns_number() + 1):
                if date_alt <= diario.fecha_final:
                    sheet.write(row, i, date_alt.strftime("%B %Y").upper(), azure_cell)
                    date_alt = date_alt + relativedelta(months=1)

            row = 5
            first_row = row + 1

            # Dynamic content
            for line in diario.linea_diario_rpt:
                
                # Cobranza meta
                if row == 5:
                    sheet.write(row, 0, line.concepto, navy_cell)
                    date_alt_cont = diario.fecha_inicial

                    for i in range(1, get_columns_number() + 1):
                        if date_alt_cont <= diario.fecha_final:
                            sheet.write(row, i, getattr(line, f"{date_alt_cont.strftime('%B_%Y').lower()}"), black_number_cell)
                            date_alt_cont = date_alt_cont + relativedelta(months=1)

                # Descuentos del periodo
                elif row == 6 or row == 7:
                
                    sheet.write(row, 0, line.concepto, navy_cell)
                    
                    date_alt_line = diario.fecha_inicial
                    for i in range(1, get_columns_number() + 1):
                        if date_alt_line <= diario.fecha_final:
                            sheet.write(row, i, getattr(line, f"{date_alt_line.strftime('%B_%Y').lower()}"), red_number_cell)
                            date_alt_line = date_alt_line + relativedelta(months=1)

                # Cobranza meses anteriores
                else:
                    sheet.write(row, 0, line.concepto, black_text_cell)
                    
                    date_alt_normal = diario.fecha_inicial
                    for i in range(1, get_columns_number() + 1):
                        if date_alt_normal <= diario.fecha_final:
                            sheet.write(row, i, getattr(line, f"{date_alt_normal.strftime('%B_%Y').lower()}"), black_number_cell)
                            date_alt_normal = date_alt_normal + relativedelta(months=1)

                row += 1

            
            # Write a conditional format over a range B9:M20.
            sheet.conditional_format('B9:AK20', {'type': 'cell',
                                         'criteria': '!=',
                                         'value': 0,
                                         'format': red_number_cell})

            # Write another conditional format over the same range.
            sheet.conditional_format('B9:AK20', {'type': 'cell',
                                         'criteria': '==',
                                         'value': 0,
                                         'format': black_number_cell})


            # SALDO POR COBRAR - EXAMPLE ENERO: SUM(B9:B20)
            row = 20
            sheet.write(row, 0, 'Saldo por cobrar', crimson_text_cell)
            date_alt_saldos = diario.fecha_inicial
            for i in range(1, get_columns_number() + 1):
                if date_alt_saldos <= diario.fecha_final:
                    sheet.write(row, i, f'=SUM({col_range[i-1]}' + str(first_row) + f':{col_range[i-1]}' + str(row)+ ')', crimson_number_cell)


            # SALDO ENTRE META POR 100 - EXAMPLE ENERO: (B21/B6) el *100 se agrega con el formato de celda
            row = 21
            sheet.write(row, 0, '% Saldo por cobrar/Vencimientos netos', black_text_cell)
            
            for i in range(1, get_columns_number() + 1):
                if date_alt_saldos <= diario.fecha_final:
                    sheet.write(row, i, f'=SI.ERROR(({col_range[i-1]}' + str(row) + f'/{col_range[i-1]}' + str(first_row) + '),0.00)', black_percent_cell)

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