from odoo import api, fields, models
import locale
from datetime import date, datetime
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
        
        cobranza_meta = []
        facturas_mes = {}
        
        vals = {
            "enero_2022": [],
            "febrero_2022": [],
            "marzo_2022": [],
            "abril_2022": [],
            "mayo_2022": [],
            "junio_2022": [],
            "julio_2022": [],
            "agosto_2022": [],
            "septiembre_2022": [],
            "octubre_2022": [],
            "noviembre_2022": [],
            "diciembre_2022": [],
            
            "enero_2023": [],
            "febrero_2023": [],
            "marzo_2023": [],
            "abril_2023": [],
            "mayo_2023": [],
            "junio_2023": [],
            "julio_2023": [],
            "agosto_2023": [],
            "septiembre_2023": [],
            "octubre_2023": [],
            "noviembre_2023": [],
            "diciembre_2023": [],
            
            "enero_2024": [],
            "febrero_2024": [],
            "marzo_2024": [],
            "abril_2024": [],
            "mayo_2024": [],
            "junio_2024": [],
            "julio_2024": [],
            "agosto_2024": [],
            "septiembre_2024": [],
            "octubre_2024": [],
            "noviembre_2024": [],
            "diciembre_2024": [],
        }
            
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
            
            date_cell = workbook.add_format({'num_format': 'yyyy-mm-dd', 'font_color': 'black', 'align': 'center'})

            # Function to get selected companies
            def get_selected_companies(self):
                companies = self.env['res.company'].browse(self.env.context.get('allowed_company_ids', []))
                company_names = [company.name for company in companies]
                return company_names
            
            # Getting number of filtered months
            def get_columns_number():
                start = diario.fecha_inicial
                end = diario.fecha_final
                
                months = (end.year - start.year) * 12 + end.month - start.month + 1
                return months
            
            

            sheet = workbook.add_worksheet('Saldos por cobrar')
            sheet.merge_range('A1:M1', diario.name, workbook.add_format({'bold': True}))

            # Company names
            sheet.merge_range('A2:M2', ', '.join(get_selected_companies(self)), workbook.add_format({'bold': True}))  

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
                            cobranza_meta.append(getattr(line, f"{date_alt_cont.strftime('%B_%Y').lower()}"))
                            date_alt_cont = date_alt_cont + relativedelta(months=1)

                # Descuentos del periodo
                elif row == 6 or row == 7:
                
                    sheet.write(row, 0, line.concepto, navy_cell)
                    
                    date_alt_line = diario.fecha_inicial
                    for i in range(1, get_columns_number() + 1):
                        if date_alt_line <= diario.fecha_final:
                            sheet.write(row, i, getattr(line, f"{date_alt_line.strftime('%B_%Y').lower()}"), red_number_cell)
                            vals[f"{date_alt_line.strftime('%B_%Y').lower()}"].append(getattr(line, f"{date_alt_line.strftime('%B_%Y').lower()}"))
                            date_alt_line = date_alt_line + relativedelta(months=1)

                # Cobranza meses anteriores
                else:
                    sheet.write(row, 0, line.concepto, black_text_cell)
                    
                    date_alt_normal = diario.fecha_inicial
                    for i in range(1, get_columns_number() + 1):
                        if date_alt_normal <= diario.fecha_final:
                            sheet.write(row, i, getattr(line, f"{date_alt_normal.strftime('%B_%Y').lower()}"), black_number_cell)
                            vals[f"{date_alt_normal.strftime('%B_%Y').lower()}"].append(getattr(line, f"{date_alt_normal.strftime('%B_%Y').lower()}"))
                            date_alt_normal = date_alt_normal + relativedelta(months=1)

                row += 1

            
            # Write a conditional format over a range B9:M20.
            sheet.conditional_format(f'B9:{col_range[get_columns_number()-1]}20', {'type': 'cell',
                                         'criteria': '!=',
                                         'value': 0,
                                         'format': red_number_cell})

            # Write another conditional format over the same range.
            sheet.conditional_format(f'B9:{col_range[get_columns_number()-1]}20', {'type': 'cell',
                                         'criteria': '==',
                                         'value': 0,
                                         'format': black_number_cell})


            # SALDO POR COBRAR - EXAMPLE ENERO: SUM(B9:B20)
            row = 20
            sheet.write(row, 0, 'Saldo por cobrar', crimson_text_cell)
            date_alt_saldos = diario.fecha_inicial
            for i in range(1, get_columns_number() + 1):
                if date_alt_saldos <= diario.fecha_final:
                    sheet.write_formula(row, i, f'=SUM({col_range[i-1]}' + str(first_row) + f':{col_range[i-1]}' + str(row)+ ')', crimson_number_cell)


            # SALDO ENTRE META POR 100 - EXAMPLE ENERO: (B21/B6) el *100 se agrega con el formato de celda
            row = 21
            sheet.write(row, 0, '% Saldo por cobrar/Vencimientos netos', black_text_cell)
            
            for i in range(1, get_columns_number() + 1):
                if date_alt_saldos <= diario.fecha_final:
                    try:
                        value = sum(vals[f"{date_alt_saldos.strftime('%B_%Y').lower()}"]) + cobranza_meta[i-1]
                        sheet.write_formula(row, i, f'{(value / cobranza_meta[i-1])}', black_percent_cell)
                    except Exception as e:
                        sheet.write_formula(row, i, f'0.00', black_percent_cell)

                    date_alt_saldos = date_alt_saldos + relativedelta(months=1)

            # -------------------
            
            sheet = workbook.add_worksheet('Desglose de ordenes')

            sheet.write(0, 0, 'Desglose de ordenes', workbook.add_format({'bold': True}))
            
            sheet.set_column(0, 6, 15)


            sheet.write(3, 0, 'Mes', azure_cell)
            sheet.write(3, 1, 'Fecha', azure_cell)
            sheet.write(3, 2, 'Fecha de vencimiento', azure_cell)
            sheet.write(3, 3, 'Ref. nota', azure_cell)
            sheet.write(3, 4, 'Cliente', azure_cell)
            sheet.write(3, 5, 'Total', azure_cell)
            row = 4

            for line in diario.linea_desglose_ordenes:
                sheet.write(row, 0, line.concepto, black_text_cell)
                sheet.write(row, 1, line.date_order, date_cell)
                sheet.write(row, 2, line.date_order_due, date_cell)
                sheet.write(row, 3, line.order_folio)
                sheet.write(row, 4, line.partner_id.name)
                sheet.write(row, 5, line.amount_total, black_number_cell)
                row += 1

            # -------------------

            sheet = workbook.add_worksheet('Desglose de facturas')

            sheet.write(0, 0, 'Desglose de facturas', workbook.add_format({'bold': True}))
            sheet.set_column(0, 11, 15)

            sheet.write(3, 0, 'Mes', azure_cell)
            sheet.write(3, 1, 'Número', azure_cell)
            sheet.write(3, 2, 'Folio fiscal', azure_cell)
            sheet.write(3, 3, 'Nombre del cliente', azure_cell)
            sheet.write(3, 4, 'Fecha de la factura', azure_cell)
            sheet.write(3, 5, 'Fecha de vencimiento', azure_cell)
            sheet.write(3, 6, 'Total', azure_cell)
            sheet.write(3, 7, 'Importe pendiente', azure_cell)
            sheet.write(3, 8, 'Facturación electronica', azure_cell)
            sheet.write(3, 9, 'Estado del pago', azure_cell)
            sheet.write(3, 10, 'Estado', azure_cell)
            row = 4

            for line in diario.linea_desglose_facturas:
                sheet.write(row, 0, line.concepto, black_text_cell)
                sheet.write(row, 1, line.name)
                sheet.write(row, 2, line.l10n_mx_edi_cfdi_uuid)
                sheet.write(row, 3, line.invoice_partner_display_name)
                sheet.write(row, 4, line.invoice_date, date_cell)
                sheet.write(row, 5, line.invoice_date_due, date_cell)
                sheet.write(row, 6, line.amount_total, black_number_cell)
                sheet.write(row, 7, line.amount_residual_signed, black_number_cell)
                sheet.write(row, 8, line.edi_state)
                sheet.write(row, 9, line.payment_state)
                sheet.write(row, 10, line.state)
                row += 1

                # ------------------- Invoices pages by month                                                                                                                                                                                                    ages by month-year -------------------
                # Formatted name
                month_name = f'{line.concepto}_{line.invoice_date_due.year}'
                
                # Dict with invoice data
                line_data = {
                    'concepto': month_name,
                    'numero': line.name,
                    'folio_fiscal': line.l10n_mx_edi_cfdi_uuid,
                    'nombre_cliente': line.invoice_partner_display_name,
                    'fecha_factura': line.invoice_date,
                    'fecha_vencimiento': line.invoice_date_due,
                    'total': line.amount_total,
                    'importe_pendiente': line.amount_residual_signed,
                    'facturacion_electronica': line.edi_state,
                    'estado_pago': line.payment_state,
                    'estado': line.state,
                    'empresa': line.company
                }
                
                # Chek if month exists
                if month_name not in facturas_mes:
                    facturas_mes[f'{month_name}'] = [line_data]
                else:
                    # Append data to month if not exists
                    facturas_mes[f'{month_name}'].append(line_data)
            
            # Create a sheet for each month
            for month in facturas_mes:
                # #  'fecha_vencimiento' to datetime
                for data in facturas_mes[month]:
                    data['fecha_vencimiento'] = datetime.strptime(data['fecha_vencimiento'].strftime('%Y-%m-%d'), '%Y-%m-%d').date()
                facturas_mes[month] = sorted(facturas_mes[month], key=lambda x: (-x['importe_pendiente'],x['fecha_vencimiento']))
                sheet_title = month.replace('_', ' ')
                sheet = workbook.add_worksheet(f'{sheet_title}')
                
                sheet.write(0, 0, f'Desglose de facturas {sheet_title}', workbook.add_format({'bold': True}))
                sheet.set_column(0, 11, 20)
                
                sheet.write(3, 0, 'Mes', azure_cell)
                sheet.write(3, 1, 'Número', azure_cell)
                sheet.write(3, 2, 'Folio fiscal', azure_cell)
                sheet.write(3, 3, 'Nombre del cliente', azure_cell)
                sheet.write(3, 4, 'Fecha de la factura', azure_cell)
                sheet.write(3, 5, 'Fecha de vencimiento', azure_cell)
                sheet.write(3, 6, 'Total', azure_cell)
                sheet.write(3, 7, 'Importe pendiente', azure_cell)
                sheet.write(3, 8, 'Facturación electronica', azure_cell)
                sheet.write(3, 9, 'Estado del pago', azure_cell)
                sheet.write(3, 10, 'Estado', azure_cell)
                sheet.write(3, 11, 'Empresa', azure_cell)
                row = 4
                
                # Iterate over each line
                data_list = facturas_mes[month]
                for fact in data_list:
                    sheet.write(row, 0, fact['concepto'].replace('_', ' '), black_text_cell)
                    sheet.write(row, 1, fact['numero'])
                    sheet.write(row, 2, fact['folio_fiscal'])
                    sheet.write(row, 3, fact['nombre_cliente'])
                    sheet.write(row, 4, fact['fecha_factura'], date_cell)
                    sheet.write(row, 5, fact['fecha_vencimiento'].strftime('%Y-%m-%d'), date_cell)
                    sheet.write(row, 6, fact['total'], black_number_cell)
                    sheet.write(row, 7, fact['importe_pendiente'], black_number_cell)
                    sheet.write(row, 8, fact['facturacion_electronica'])
                    sheet.write(row, 9, fact['estado_pago'])
                    sheet.write(row, 10, fact['estado'])
                    sheet.write(row, 11, fact['empresa'])
                    row += 1