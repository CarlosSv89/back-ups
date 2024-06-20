from odoo import api, fields, models
import locale
import logging
locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
_logger = logging.getLogger(__name__)
class pdvReport(models.Model):
    _name = 'report.reporte_li'
    _inherit = 'report.report_xlsx.abstract'
    _description = 'Libro de ingresos'

    
    def generate_xlsx_report(self, workbook, data, reporte):
        for ctrl in reporte:
            linesByDate = {}
            cobranzas = {}
            traspasos = []
            cruces = []
            
            report_name = ctrl.name
            titulo = workbook.add_format({'bold': True, 'font_name': 'Century Gothic', 'bg_color': '#00b0f0', 'font_color': 'white', 'font_size': 12})
            titulo_wrap = workbook.add_format({'bold': True, 'font_name': 'Century Gothic', 'bg_color': '#00b0f0', 'font_color': 'white', 'font_size': 12,'text_wrap': True, 'border': 1, 'align': 'center', 'valign': 'vcenter'})
            saldo = workbook.add_format({'font_name': 'Century Gothic','num_format':'#,##0.00', 'bold': True, 'font_color': 'red'})
            
            #formato para celdas
            format_cell = workbook.add_format({'font_color': 'black','font_name': 'Century Gothic','border': True, 'border_color': 'black','num_format':'#,##0.00'})
            format_cell_b = workbook.add_format({'bold': True, 'font_color': 'black','font_name': 'Century Gothic','border': True, 'border_color': 'black','num_format':'#,##0.00'})
            format_cell_b_red = workbook.add_format({'bold': True, 'font_color': 'red','font_name': 'Century Gothic','border': True, 'border_color': 'black','num_format':'#,##0.00'})

            format_cell_date_b = workbook.add_format({'bold': True, 'font_color': 'black','font_name': 'Century Gothic','border': True, 'border_color': 'black','num_format': 'dd-mmm-yyyy', 'font_size': 12})
            format_cell_date_b_alt = workbook.add_format({'font_color': 'black','font_name': 'Century Gothic','border': True, 'border_color': 'black','num_format': 'dd-mmm-yyyy', 'font_size': 12})
            format_cell_date = workbook.add_format({'font_color': 'black','font_name': 'Century Gothic','border': True, 'border_color': 'black','num_format': 'dd/mm/yyyy', 'font_size': 12})

            format_sign = workbook.add_format({'font_color': 'black','font_name': 'Century Gothic', 'border_color': 'black', 'align': 'center'})
            format_sign.set_top(1)
            
            sheet = workbook.add_worksheet('LIBRO_BANCARIO')
            
            # set background color
            colList = ['A','B','C','D','E','F','G','H']
            for col in colList:
                for n in range(1,8):
                    sheet.write(col+str(n), '', titulo)
            sheet.write('A1', 'GAS SILZA SA DE CV', titulo)
            sheet.write('A2', 'Libro de Cuenta Bancaria de ingresos', titulo)
            sheet.write('A3', f'ID: {ctrl.id}', titulo)
            sheet.write('A4', ctrl.planta.name, titulo)
            sheet.write('A5', f'BBVA {ctrl.cuenta.name}', titulo)
            
            sheet.write('A7', 'FECHA CONCILIACION', titulo_wrap)
            sheet.write('B7', 'CONTADO O COBRANZA', titulo_wrap)
            sheet.write('C7', 'FECHA DE MOVIMIENTO', titulo_wrap)
            sheet.write('D7', 'TIPO', titulo_wrap)
            sheet.write('E7', 'PARCIALES', titulo_wrap)
            sheet.write('F7', 'CARGO', titulo_wrap)
            sheet.write('G7', 'ABONO', titulo_wrap)
            sheet.write('H7', 'SALDO', titulo_wrap)
            
            sheet.write('A8', 'SALDO INICIAL (SALDO ANTERIOR)', None)
            sheet.write('H8', ctrl.saldo_inicial, format_cell_b)

            sheet.set_column(0, 0, 20)
            sheet.set_column(1, 1, 16)
            sheet.set_column(2, 2, 15)
            sheet.set_column(3, 3, 45)
            sheet.set_column(4, 4, 15)
            sheet.set_column(5, 5, 15)
            sheet.set_column(6, 6, 15)
            sheet.set_column(7, 7, 20)

            row = 8
            
            for line in ctrl.linea_libro_ids:
                #format date to dd-Mon-YYYY
                line_date = line.fecha.strftime('%d-%b-%Y')
                if line.ingreso == 'Cobranza':
                    if line_date not in cobranzas:
                        cobranzas[line_date] = [line]
                        if line_date not in linesByDate:
                            linesByDate[line_date] = []
                    else:
                        cobranzas[line_date].append(line)
                        linesByDate[line_date] = []
                elif line.ingreso == 'CRUCE CUENTAS':
                    cruces.append(line)
                
                elif line.ingreso == False:
                    traspasos.append(line)
                else:
                    if line_date not in linesByDate:
                        linesByDate[line_date] = [line]
                    else:
                        linesByDate[line_date].append(line)

            # order linesByDate ascending
            linesByDate = dict(sorted(linesByDate.items()))

            # for date in linesByDate:
            #     linesByDate[date] = sorted(linesByDate[date], key=lambda x: x.debe, reverse=True)
            # _logger.error(linesByDate)
            
            sumByDate = lambda date: sum([line.debe for line in linesByDate[date]])
            sumCobranza = lambda date: sum([cobranza.debe for cobranza in cobranzas[date]])
            
            # fecha_final as fecha conciliacion
            sheet.write(row, 0, ctrl.fecha_final.strftime('%d-%b-%Y'), format_cell_date_b)
            
            # start with the lines
            for date in linesByDate:
                if len(linesByDate[date]) > 0:
                    sheet.write(row, 1, '', format_cell)
                    sheet.write(row, 2, '', format_cell)
                    sheet.write(row, 3 , f"VENTA DEL DIA {linesByDate[date][0].fecha.strftime('%d/%m/%Y')}", format_cell_b)
                    sheet.write(row, 4, '', format_cell)
                    sheet.write(row, 5 , sumByDate(date), format_cell)
                    sheet.write(row, 6, '', format_cell)
                    sheet.write_formula(row, 7, f'=+H{row}+F{row+1}-G{row+1}', format_cell_b)
                    row += 1
                    for line in linesByDate[date]:
                        sheet.write(row, 0, '', format_cell)
                        sheet.write(row, 1 , line.ingreso.upper(), format_cell)
                        sheet.write(row, 2 , line.fecha_rda.strftime('%d-%b-%Y'), format_cell_date_b_alt)
                        sheet.write(row, 3 , line.descripcion.upper(), format_cell)
                        sheet.write(row, 4 , line.debe, format_cell)
                        sheet.write(row, 5, '', format_cell)
                        sheet.write(row, 6, '', format_cell)
                        sheet.write_formula(row, 7, f'=+H{row}+F{row+1}-G{row+1}', format_cell_b)
                        row += 1
                if date in cobranzas:
                    sheet.write(row, 0, '', format_cell)
                    sheet.write(row, 1 , '', format_cell)
                    sheet.write(row, 2 , '', format_cell_b)
                    sheet.write(row, 3 , f"COBRANZA DEL DIA {cobranzas[date][0].fecha.strftime('%d/%m/%Y')}", format_cell_b)
                    sheet.write(row, 4 , '', format_cell)
                    sheet.write(row, 5, sumCobranza(date), format_cell)
                    sheet.write(row, 6, '', format_cell)
                    sheet.write_formula(row, 7, f'=+H{row}+F{row+1}-G{row+1}', format_cell_b)
                    row += 1
                    for cobranza in cobranzas[date]:
                        sheet.write(row, 0, '', format_cell)
                        sheet.write(row, 1 , cobranza.ingreso.upper(), format_cell)
                        sheet.write(row, 2 , cobranza.fecha_rda.strftime('%d-%b-%Y'), format_cell_date_b_alt)
                        sheet.write(row, 3 , cobranza.descripcion.upper(), format_cell)
                        sheet.write(row, 4 , cobranza.debe, format_cell)
                        sheet.write(row, 5, '', format_cell)
                        sheet.write(row, 6, '', format_cell)
                        sheet.write_formula(row, 7, f'=+H{row}+F{row+1}-G{row+1}', format_cell_b)
                        row += 1
            if len(traspasos) > 0:
                for traspaso in traspasos:
                    sheet.write(row, 0, '', format_cell)
                    sheet.write(row, 1 , '', format_cell)
                    sheet.write(row, 2 , traspaso.fecha_rda.strftime('%d-%b-%Y'), format_cell_date_b_alt)
                    sheet.write(row, 3 , traspaso.descripcion.upper(), format_cell)
                    sheet.write(row, 4 , traspaso.haber, format_cell)
                    sheet.write(row, 5, '', format_cell)
                    sheet.write(row, 6, traspaso.haber, format_cell)
                    sheet.write_formula(row, 7, f'=+H{row}+F{row+1}-G{row+1}', format_cell_b)
                    row += 1
            if len(cruces) > 0:
                for cruce in cruces:
                    sheet.write(row, 0, '', format_cell)
                    sheet.write(row, 1 , '', format_cell)
                    sheet.write(row, 2 , cruce.fecha_rda.strftime('%d-%b-%Y'), format_cell_date_b_alt)
                    sheet.write(row, 3 , cruce.descripcion.upper(), format_cell)
                    sheet.write(row, 4 , cruce.debe if cruce.debe > 0 else cruce.haber, format_cell)
                    sheet.write(row, 5, cruce.debe if cruce.debe > 0 else '', format_cell)
                    sheet.write(row, 6, cruce.haber if cruce.haber > 0 else '', format_cell)
                    sheet.write_formula(row, 7, f'=+H{row}+F{row+1}-G{row+1}', format_cell_b)
                    row += 1
            sheet.write(row, 0, 'SALDO FINAL', format_cell)
            sheet.write(row, 1, '', format_cell)
            sheet.write(row, 2, '', format_cell)
            sheet.write(row, 3, '', format_cell)
            sheet.write(row, 4, '', format_cell)
            sheet.write(row, 5, '', format_cell)
            sheet.write(row, 6, '', format_cell)
            sheet.write_formula(row, 7, f'=+H{row}+F{row+1}-G{row+1}', format_cell_b)
            
            # add condition at the end to get the last row
            sheet.conditional_format(f'H8:H{row+1}', {'type': 'cell',
                                         'criteria': '<',
                                         'value': 0,
                                         'format': format_cell_b_red})
            
            
            sheet.merge_range(f"B{row+4}:C{row+4}", 'ELABORÓ', format_sign)
            sheet.merge_range(f"F{row+4}:H{row+4}", 'SUPERVISÓ', format_sign)
            workbook.close()


