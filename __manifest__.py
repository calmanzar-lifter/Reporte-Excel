{
    'name': 'DGT-2 Overtime Report',
    'version': '1.0.0',
    'category': 'Human Resources',
    'summary': 'Exports detailed DGT-2 format overtime reports, including costs, to Excel.',
    'description': 'The module exports detailed DGT-2 format overtime reports, including costs, to Excel, streamlining compliance and optimizing resource management.',
    'depends': ['hr_payroll'],
    'author': 'Frainer Encarnación',
    'website': 'https://fraineralex.dev',
    'data': [
        'wizard/dgt2_report_wizard_view.xml',
        'security/ir.model.access.csv'
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'LGPL-3'
}
