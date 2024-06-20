from odoo import api, fields, models


class DiarioAntiguedadSaldosReporte(models.Model):
    _name = 'report.rep.diario.antiguedad.saldos.report'
    _description = 'Reporte de saldos por cobrar'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, diarios):
        for diario in diarios:
            sheet = workbook.add_worksheet(diario.name)
            sheet.write(0, 0, diario.name, workbook.add_format({'bold': True}))
            format_header = workbook.add_format({'bold': True, 'bg_color': '#222A35', 'font_color': 'white'})
            sheet.write(3, 0, 'Cliente', format_header)
            sheet.write(3, 1, 'Días crédito', format_header)
            sheet.write(3, 2, 'Subtotal', format_header)
            sheet.write(3, 3, 'Al corriente', format_header)
            sheet.write(3, 4, 'Vencido', format_header)
            sheet.write(3, 5, '1-15 Días', format_header)
            sheet.write(3, 6, '16-30 Días', format_header)
            sheet.write(3, 7, '31-60 Días', format_header)
            sheet.write(3, 8, '61-90 Días', format_header)            
            sheet.write(3, 9, '91 a mas días', format_header)
            sheet.write(3, 10, 'Saldo a favor', format_header)
            sheet.write(3, 11, 'Saldo total', format_header)
            sheet.write(3, 12, 'Clasificación', format_header)
            row = 4
            format_cell = workbook.add_format({'bold': True, 'bg_color': '#92D050'})
            for line in diario.linea_diario_ids:
                sheet.write(row, 0, line.partner_id.name, format_cell)
                sheet.write(row, 1, line.dias_credito.name)
                sheet.write(row, 2, line.subtotal)
                sheet.write(row, 3, line.al_corriente)
                sheet.write(row, 4, line.vencido)
                sheet.write(row, 5, line.vencido_1_15)
                sheet.write(row, 6, line.vencido_16_30)
                sheet.write(row, 7, line.vencido_31_60)
                sheet.write(row, 8, line.vencido_61_90)
                sheet.write(row, 9, line.vencido_91_mas)
                sheet.write(row, 10, line.saldo_favor)
                sheet.write(row, 11, line.saldo_total)
                sheet.write(row, 12, line.clasificacion)
                row += 1
                