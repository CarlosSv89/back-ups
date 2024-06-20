from odoo import api, fields, models

class pdvReport(models.Model):
    _name = 'report.reporte_li'
    _inherit = 'report.report_xlsx.abstract'
    _description = 'Libro de ingresos'

    
    def generate_xlsx_report(self, workbook, data, reporte):
        for ctrl in reporte:
            report_name = ctrl.name
            # One sheet by partner
            #image_path = "evaluacion_y_compensacion,images/grupo_tomza.jpg"  # Replace with the actual path to your image
            #sheet.insert_image('A1', image_path, {'x_offset': 15, 'y_offset': 10})
            titulo = workbook.add_format({'bold': True, 'font_name': 'Century Gothic', 'bg_color': '#00b0f0', 'font_color': 'white'})
            # titulo.set_font_size(36)
            subtitulo = workbook.add_format({'bold': True, 'font_name': 'Century Gothic'})
            subtitulo.set_font_size(24)
            subtitulo_date = workbook.add_format({'bold': True, 'font_name': 'Century Gothic','num_format': 'dd-mm-yyyy'})
            subtitulo_date.set_font_size(24)
            subtitulo_saldo = workbook.add_format({'bold': True, 'font_name': 'Century Gothic','num_format':'_* #,##0.00_-;-$* #,##0.00_-;_* "-"??_-;_-@_-'})
            subtitulo_saldo.set_font_size(24)

            sheet = workbook.add_worksheet(report_name[:31])
            
            sheet.merge_range("A1:I1", 'GAS SILZA SA DE CV', titulo)

            sheet.write('A2', 'EMPRESA (PLANTA): ', subtitulo)
            sheet.write('B2', ctrl.planta.name, subtitulo)

            sheet.write('A3', 'LIBRO DE BANCOS: ', subtitulo)
            sheet.write('B3', ctrl.fecha_libro, subtitulo_date)

            sheet.write('A4', 'SALDO INICIAL: ', subtitulo)
            sheet.write('B4', ctrl.saldo_inicial, subtitulo_saldo)

            sheet.set_column(0, 0, 50)
            sheet.set_column(1, 1, 35)
            sheet.set_column(2, 2, 20)
            sheet.set_column(3, 3, 20)
            sheet.set_column(4, 4, 20)
            sheet.set_column(5, 5, 35)
            sheet.set_column(6, 6, 20)
            sheet.set_column(7, 7, 20)
            sheet.set_column(8, 8, 20)

            #formato para celdas
            format_cell_head = workbook.add_format({'bold': True,'font_color': 'white','font_name': 'Lato', 'bg_color': '#990000','border': True, 'border_color': 'black'})
            format_cell_head.set_font_size(12)
            format_cell = workbook.add_format({'font_color': 'black','font_name': 'Lato', 'bg_color': '#f2f2f2','border': True, 'border_color': 'black','num_format':'$* #,##0.00;-$* #,##0.00;""??;@'})
            format_cell.set_font_size(12)
            format_cell_date = workbook.add_format({'font_color': 'black','font_name': 'Lato', 'bg_color': '#f2f2f2','border': True, 'border_color': 'black','num_format': 'dd-mm-yyyy'})
            format_cell_date.set_font_size(12)
            format_cell_account = workbook.add_format({'font_color': 'black','font_name': 'Lato', 'bg_color': '#f2f2f2','border': True, 'border_color': 'black'})
            format_cell_account.set_font_size(12)

            # sheet.write('A5', 'Fecha', format_cell_head)
            # sheet.write('B5', 'Ingreso', format_cell_head)
            # sheet.write('C5', 'Fecha RDA', format_cell_head)
            # sheet.write('D5', 'Banco', format_cell_head)
            # sheet.write('E5', 'No. Cuenta', format_cell_head)
            # sheet.write('F5', 'Descripción', format_cell_head)
            # sheet.write('G5', 'Debe', format_cell_head)
            # sheet.write('H5', 'Haber', format_cell_head)
            # sheet.write('I5', 'Saldo', format_cell_head)

            # column_row = 5

            # for line in ctrl.linea_libro_ids:
            #     sheet.write(column_row,0, line.fecha, format_cell_date)
            #     sheet.write(column_row,1, line.ingreso, format_cell)
            #     sheet.write(column_row,2, line.fecha_rda, format_cell_date)
            #     sheet.write(column_row,3, line.banco, format_cell)
            #     sheet.write(column_row,4, line.no_cuenta, format_cell_account)
            #     sheet.write(column_row,5, line.descripcion, format_cell_account)
            #     sheet.write(column_row,6, line.debe, format_cell)
            #     sheet.write(column_row,7, line.haber, format_cell)
            #     sheet.write(column_row,8, line.saldo, format_cell)

            #     column_row = column_row + 1


