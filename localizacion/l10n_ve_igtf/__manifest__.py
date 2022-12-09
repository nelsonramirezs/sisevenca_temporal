# -*- coding: utf-8 -*-
{
    'name': ' Venezuela - IGTF',
    'version': '15.0.1.0',
    'author': 'Bryan Gomez',
    'contributor': "Bryan Gómez <bryan.gomez1311@gmail.com>",
    'summary': '',
    'description': """""",
    'category': 'Accounting/Accounting',
    'website': '',
    'depends': ['account', 'l10n_ve_account', 'l10n_ve_account_sequence_number', 'l10n_ve_payment_method'],
    'data': [
            'security/ir.model.access.csv',
            'data/ir_sequence.xml',
            'report/paperformat.xml',
            'report/ir_action_report.xml',
            'views/account_journal_views.xml',
            'views/account_move_views.xml',
            'views/account_payment_method_views.xml',
            'views/account_payment_views.xml',
            'views/report_resume_invoice_igtf.xml',
            'wizard/resume_igtf_wizard_views.xml',
    ],
    'license': 'LGPL-3',
    'installable': True,
    'application': True,
    'auto_install': False,
}

