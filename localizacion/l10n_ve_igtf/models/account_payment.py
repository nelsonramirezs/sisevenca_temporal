# -*- coding: utf-8 -*-

from odoo import api, fields, models


class AccountPayment(models.Model):
    _inherit = "account.payment"

    move_payment_igtf = fields.Many2one('account.move')
    move_provider_igtf = fields.Many2one('account.move')
    amount_retention_payment = fields.Monetary(string='Monto por metodo de pago igtf', currency_field='currency_id',
                                               compute='compute_amount_payment_retention', readonly=True, store=True)

    amount_retention_journal = fields.Monetary(string='Monto por diario igtf', currency_field='currency_id',
                                               compute='compute_amount_payment_retention', readonly=True, store=True)

    def action_post(self):
        res = super(AccountPayment, self).action_post()
        self.action_retention_igtf_journal()
        self.action_retention_igtf_payment()
        return res

    def action_draft(self):
        res = super(AccountPayment, self).action_draft()
        self.move_payment_igtf.filtered(lambda move: move.state == 'posted').button_draft()
        self.move_payment_igtf.with_context(force_delete=True).unlink()
        self.move_provider_igtf.filtered(lambda move: move.state == 'posted').button_draft()
        self.move_provider_igtf.with_context(force_delete=True).unlink()
        return res

    @api.depends('currency_id', 'payment_method_line_id', 'amount')
    def compute_amount_payment_retention(self):
        retention = 0.0
        amount_base = 0.0
        for payment in self:
            if payment.payment_method_line_id.payment_method_id.is_igtf:
                if payment.currency_id.id == payment.env.company.currency_id.id:
                    amount_base += payment.amount
                    retention += amount_base * payment.payment_method_line_id.payment_method_id.percentage / 100
                    payment.write({'amount_retention_payment': retention})
                if payment.currency_id.id != payment.env.company.currency_id.id:
                    amount_base += payment.amount * payment.os_currency_rate
                    retention += amount_base * payment.payment_method_line_id.payment_method_id.percentage / 100
                    payment.write({'amount_retention_payment': retention})

            if payment.journal_id.type_bank == 'national':
                retention_rate = 0.0
                amount_base_rate = 0.0
                if payment.currency_id.id == payment.env.company.currency_id.id:
                    amount_base_rate += payment.amount
                    retention_rate += amount_base * payment.journal_id.percentage / 100
                    payment.write({'amount_retention_journal': retention})
                if payment.currency_id.id != payment.env.company.currency_id.id:
                    amount_base_rate += payment.amount * payment.os_currency_rate
                    retention_rate += amount_base * payment.journal_id.percentage / 100
                    payment.write({'amount_retention_journal': retention})

    def action_retention_igtf_journal(self):
        if self.payment_type == 'outbound' and self.partner_type == 'supplier' and self.journal_id.type_bank == 'national':
            move_id = self.register_move_entry(self.amount_retention_journal, self.journal_id.journal_igtf_id)

            self.register_move_line_entry(move_id, self.amount_retention_journal, self.journal_id.account_id,
                                          self.company_id.account_journal_payment_credit_account_id)
            self.move_provider_igtf = move_id.id
            move_id.action_post()

    def action_retention_igtf_payment(self):
        if self.payment_method_line_id.payment_method_id.is_igtf:
            account_payment = self.journal_id.default_account_id if self.payment_type == "inbound" \
                else self.company_id.account_journal_payment_credit_account_id
            move_id = self.register_move_entry(self.amount_retention_payment,
                                               self.payment_method_line_id.payment_method_id.journal_id)

            self.register_move_line_entry(move_id, self.amount_retention_payment,
                                          self.payment_method_line_id.payment_method_id.account_id, account_payment)

            self.move_payment_igtf = move_id.id
            move_id.action_post()

    def register_move_entry(self, retention, journal_id):
        value = {
            'name': self.env['ir.sequence'].next_by_code('account.payment.igtf'),
            'date': self.date,
            'partner_id': self.company_id.partner_id.id,
            'journal_id': journal_id.id,
            'amount_total_signed': retention,
            'move_type': 'entry',
            'company_id': self.env.company.id,
            'currency_id': self.company_id.currency_id.id,
        }
        move_obj = self.env['account.move'].create(value)
        return move_obj

    def register_move_line_entry(self, move_id, retention, account_igtf_id, payment_account_credit):
        line = []
        line.append((0, 0, {
            'name': "IGTF/DOC-: " + self.ref,
            'ref': "Pago de IGTF %s" % (self.ref),
            'move_id': move_id.id,
            'date': self.date,
            'partner_id': self.env.company.partner_id.id,
            'account_id': account_igtf_id.id if self.payment_type == "inbound" else payment_account_credit.id,
            'credit': retention,
            'debit': 0.0,
            'balance': -retention,
            'price_unit': retention,
            'price_subtotal': retention,
            'price_total': retention,
            'currency_id': self.currency_id.id if self.currency_id.id != self.company_currency_id.id else "",
            'amount_currency': -1 * self.amount if self.currency_id.id != self.company_currency_id.id else "",
        }))
        line.append((0, 0, {
            'name': "IGTF/DOC-: " + self.ref,
            'ref': "Pago de IGTF %s" % (self.ref),
            'move_id': move_id.id,
            'date': self.date,
            'partner_id': self.env.company.partner_id.id,
            'account_id': account_igtf_id.id if self.payment_type == "outbound" else payment_account_credit.id,
            'credit': 0.0,
            'debit': retention,
            'balance': retention,
            'price_unit': retention,
            'price_subtotal': retention,
            'price_total': retention,
            'currency_id': self.currency_id.id if self.currency_id.id != self.company_currency_id.id else "",
            'amount_currency': self.amount if self.currency_id.id != self.company_currency_id.id else "",
        }))
        move_line = move_id.write({'line_ids': line})
        return move_line

