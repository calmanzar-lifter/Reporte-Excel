from odoo import models, fields
import xlwt
import base64
import io

TITLE = 'Reporte de Cambios Salariales'


class SalaryChangesReportWizard(models.TransientModel):
    _name = 'salary.changes.report.wizard'
    _description = 'Reporte de Cambios Salariales'

    company_id = fields.Many2one('res.company',
                                 'Compañía',
                                 default=lambda self: self.env.company.id,
                                 required=True, readonly=True)

    employee_ids = fields.Many2many('hr.employee',
                                    string="Empleados Incluidos", domain="[('company_id', '=?', company_id)]")

    def generate_report(self):
        slip_line_ids = self.env['hr.payslip.line'].search([
            ('slip_id.employee_id', 'in', self.employee_ids.ids),
            ('slip_id.company_id', '=?', self.company_id.id),
            ('salary_rule_id.code', 'in', ['BASIC', 'BISA']),
            ('slip_id.state', '=', 'done'),
            ('slip_id.net_wage', '>', '0'),
            ('total', '>', '0'),
        ])

        title = f'{TITLE} - {self.company_id.name}'

        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet(title)
        column_width = 256 * 30
        xlwt.add_palette_colour("silver", 0x21)
        workbook.set_colour_RGB(0x21, 211, 221, 227)
        header_style = xlwt.easyxf(
            'font: bold on, height 200; align: horiz center; pattern: pattern solid, fore_colour silver;')

        headers = ['Contrato', 'Empleado', 'Cédula',
                   'Salario Actual', 'Salarios Anteriores']

        for col_num, header in enumerate(headers):
            worksheet.write(0, col_num, header, header_style)
            worksheet.col(
                col_num).width = column_width if header != 'Salarios Anteriores' else column_width * 3

        row_num = 1

        for employee in self.employee_ids:
            salaries = []
            all_salaries_formatted = ''
            for line in slip_line_ids:
                if line.employee_id.id == employee.id and line.total not in salaries and line.total != employee.contract_id.wage:
                    salaries.append(line.total)
                    all_salaries_formatted += f"{line.slip_id.date_to.strftime('%d-%m-%Y')}: RD${line.total}, "

            worksheet.write(row_num, 0, employee.contract_id.name or '')
            worksheet.write(row_num, 1, employee.name or '')
            worksheet.write(
                row_num, 2, employee.identification_id or '')
            worksheet.write(
                row_num, 3, f"RD${employee.contract_id.wage}" or '0.0')
            worksheet.write(
                row_num, 4, all_salaries_formatted[:-2] if all_salaries_formatted else '')

            row_num += 1

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
