# -*- coding: utf-8 -*-

from odoo import api, fields, models
import logging
_logger = logging.getLogger('__name__')


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    type_bank = fields.Selection([('foreign', 'Extranjero'), ('national', 'Nacional')], default='foreign')
    percentage = fields.Float(string="Percentage IGTF", help="El porcentaje a aplicar para retener")
    account_id = fields.Many2one('account.account', string="Cuenta IGTF", help="Esta cuenta se usará en lugar"
                                                                               "de la predeterminada uno como la cuenta"
                                                                               "por pagar para el socio actual")
    journal_igtf_id = fields.Many2one('account.journal', string="Diario para consecutivo asiento IGTF", index=True)
