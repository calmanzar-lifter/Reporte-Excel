from odoo import models, fields
import xlwt
import base64
import io

TITLE = 'Reporte de Horas Extras DGT-2'


class OvertimeReportWizard(models.TransientModel):
    _name = 'overtime.report.wizard'
    _description = 'DGT-2 Overtime Report Wizard'

    company_id = fields.Many2one('res.company',
                                 'Compañía',
                                 default=lambda self: self.env.company.id,
                                 required=True, readonly=True)

    payslip_run_ids = fields.Many2many('hr.payslip.run',
                                       string="Lotes incluidos", domain="[('company_id', '=?', company_id)]")

    def generate_report(self):
        slip_ids = self.env['hr.payslip'].search(
            [('payslip_run_id', 'in', self.payslip_run_ids.ids), ('company_id', '=?', self.company_id.id)])
        categories = self.env['hr.salary.rule.category'].search(
            [('code', '=', 'BASIC')])
        rules = self.env['hr.salary.rule'].search(
            [('category_id', 'in', categories.ids)])

        title = f'{TITLE} - {self.company_id.name}'

        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet(title)
        column_width = 256 * 30
        xlwt.add_palette_colour("silver", 0x21)
        workbook.set_colour_RGB(0x21, 211, 221, 227)
        header_style = xlwt.easyxf(
            'font: bold on, height 200; align: horiz center; pattern: pattern solid, fore_colour silver;')
        total_style = xlwt.easyxf(
            'font: bold on, height 200; pattern: pattern solid, fore_colour silver;')

        headers = ['Empleado', 'Cédula', 'Fecha', 'Salario Base']

        for col_num, header in enumerate(headers):
            worksheet.write(0, col_num, header, header_style)
            worksheet.col(col_num).width = column_width

        total_amount = 0.0
        row_num = 1

        for payslip in slip_ids:
            if payslip.net_wage < 0.0:
                continue

            for line in payslip.line_ids:
                if line.salary_rule_id in rules and line.total > 0.0:
                    worksheet.write(row_num, 0, payslip.employee_id.name)
                    worksheet.write(
                        row_num, 1, payslip.employee_id.identification_id)
                    worksheet.write(
                        row_num, 2, line.date_to.strftime('%Y-%m-%d'))
                    worksheet.write(row_num, 3, line.net_wage)

                    row_num += 1
                    total_amount += line.net_wage

        worksheet.write(row_num, 0, 'Total', total_style)
        worksheet.write(row_num, 1, '', total_style)
        worksheet.write(row_num, 2, '', total_style)
        worksheet.write(row_num, 3, total_amount, total_style)

        workbook_data = io.BytesIO()
        workbook.save(workbook_data)
        workbook_data.seek(0)
        report_file = base64.b64encode(workbook_data.getvalue())
        filename = f'{title}.xls'
        attachement = self.env['ir.attachment'].create({
            'name': filename,
            'datas': report_file,
            'mimetype': 'application/vnd.ms-excel',
            'res_model': self._name,
            'res_id': self.id
        })

        return {
            'name': filename,
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachement.id}?download=true',
            'target': 'self'
        }
