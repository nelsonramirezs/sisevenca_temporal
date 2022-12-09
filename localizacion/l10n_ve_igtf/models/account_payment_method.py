# -*- coding: utf-8 -*-

from odoo import api, models, fields, _
from odoo.exceptions import UserError


class AccountPaymentMethod(models.Model):
    _inherit = 'account.payment.method'

    is_igtf = fields.Boolean(string='Retención automática de IGTF', help="Cuando es cierto, la retención de IGTF"
                                                                        "del cliente se comprobará y"
                                                                        "validar automáticamente", default=False)
    percentage = fields.Float(string="Percentage IGTF", help="El porcentaje a aplicar para retener")
    account_id = fields.Many2one('account.account', string="Cuenta cuenta IGTF", help="Esta cuenta se usará en lugar"
                                                                                      "de la predeterminada uno como"
                                                                                      "la cuenta por cobrar"
                                                                                      "para el cliente")
    journal_id = fields.Many2one('account.journal', help="Esta cuenta se coloca de forma temporal para que haga el"
                                                         "asiento y luego se pasa al diario del pago")


class AccountPaymentMethodLine(models.Model):
    _inherit = "account.payment.method.line"

    @api.constrains('name')
    def _ensure_unique_name_for_journal(self):
        pass
        # self.flush(['name'])
        # self._cr.execute('''
        #     SELECT apml.name, apm.payment_type
        #     FROM account_payment_method_line apml
        #     JOIN account_payment_method apm ON apml.payment_method_id = apm.id
        #     WHERE apml.journal_id IS NOT NULL
        #     GROUP BY apml.name, apm.payment_type
        #     HAVING count(apml.id) > 1
        # ''')
        # res = self._cr.fetchall()
        # if res:
        #     (name, payment_type) = res[0]
        #     raise UserError(_("You can't have two payment method lines of the same payment type (%s) "
        #                       "and with the same name (%s) on a single journal.", payment_type, name))
