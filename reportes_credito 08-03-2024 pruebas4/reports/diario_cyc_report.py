from odoo import api, fields, models


class DiarioCreditoCobranzaReporte(models.Model):
    _name = 'report.rep.diario.cyc.report'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, diarios):
        for diario in diarios:
            sheet = workbook.add_worksheet(diario.name)
            sheet.write(0, 0, diario.name, workbook.add_format({'bold': True}))
            format_header = workbook.add_format({'bold': True})
            sheet.write(3, 0, 'Fecha', format_header)
            sheet.write(3, 1, 'Saldo inicial', format_header)
            sheet.write(3, 2, 'Crédito otorgado', format_header)
            sheet.write(3, 3, 'Descuentos', format_header)
            sheet.write(3, 4, 'Cobranza', format_header)
            sheet.write(3, 5, 'Subtotal', format_header)
            sheet.write(3, 6, 'Nota de cargo', format_header)
            sheet.write(3, 7, 'Cobranza nota cargo', format_header)
            sheet.write(3, 8, 'Cobranza anticipada', format_header)            
            sheet.write(3, 9, 'Ajustes fuera del periodo', format_header)
            sheet.write(3, 10, 'Saldo final', format_header)
            row = 4
            format_cell = workbook.add_format({'bold': True})
            for line in diario.linea_diario_ids:
                sheet.write_datetime(row, 0, line.date, format_cell)
                sheet.write(row, 1, line.saldo_inicial)
                sheet.write(row, 2, line.credito_otorgado)
                sheet.write(row, 3, line.descuentos)
                sheet.write(row, 4, line.cobranza)
                sheet.write(row, 5, line.subtotal)
                sheet.write(row, 6, line.nota_cargo)
                sheet.write(row, 7, line.cobranza_nota_cargo)
                sheet.write(row, 8, line.cobranza_anticipada)
                sheet.write(row, 9, line.ajuste_fuera_periodo)
                sheet.write(row, 10, line.saldo_final)
                row += 1
                