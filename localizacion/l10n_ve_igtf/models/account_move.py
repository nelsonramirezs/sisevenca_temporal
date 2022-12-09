# -*- coding: utf-8 -*-

from odoo import fields, models, api
import logging
_logger = logging.getLogger('__name__')


class AccountMove(models.Model):
    _inherit = 'account.move'

    account_igtf_ids = fields.One2many('account.payment.igtf', 'move_id', string='Cobros IGTF', readonly=True)
    tax_igtf_rate = fields.Monetary(compute="_compute_amount_all_igtf_rate", currency_field='currency_id2', store=True)
    tax_igtf = fields.Monetary(compute="_compute_amount_all_igtf", currency_field='currency_id', store=True)

    @api.depends('account_igtf_ids')
    def _compute_amount_all_igtf(self):
        amount = 0.0
        for move in self:
            for igtf in move.account_igtf_ids:
                if move.currency_id == move.company_id.currency_id:
                    amount += igtf.amount
                if move.currency_id != move.company_id.currency_id and move.os_currency_rate:
                    amount += igtf.amount / move.os_currency_rate
            move.tax_igtf = amount

    @api.depends('tax_igtf')
    def _compute_amount_all_igtf_rate(self):
        for move in self:
            if move.tax_igtf > 0.0:
                if move.currency_id == move.company_id.currency_id and move.os_currency_rate:
                    move.update({'tax_igtf_rate': move.tax_igtf / move.os_currency_rate})
                else:
                    move.update({'tax_igtf_rate': move.tax_igtf * move.os_currency_rate})

    @api.constrains('amount_total', 'amount_residual')
    def associate_move_with_out_invoice_igtf(self):
        for move in self.filtered(lambda x: x.state == 'posted' and x.move_type in ('out_invoice', 'out_refund')):
            move.account_igtf_ids.unlink()
            account_gene = move.partner_id.property_account_receivable_id.id
            for line in move.line_ids:
                if line.account_id.id == account_gene:
                    account_partial_obj = move.env['account.partial.reconcile'].search([
                        ('debit_move_id', '=', line.id)])
                    for partial in account_partial_obj:
                        amount_base = 0.0
                        amount_rate = 0.0
                        if partial.credit_move_id.move_id.payment_id.payment_method_line_id.payment_method_id.is_igtf:
                            if partial.credit_currency_id != move.company_id.currency_id:
                                amount_base += partial.amount
                                amount_rate += partial.credit_amount_currency * partial.credit_move_id.move_id.payment_id.os_currency_rate
                            if partial.credit_currency_id == move.company_id.currency_id:
                                amount_base += partial.amount
                                amount_rate += partial.amount / partial.credit_move_id.move_id.payment_id.os_currency_rate

                            vals = {
                                'move_id': move.id,
                                'move_igtf_id': partial.credit_move_id.move_id.payment_id.move_payment_igtf.id,
                                'payment_method_id': partial.credit_move_id.move_id.payment_id.payment_method_line_id.payment_method_id.id,
                                'amount_rate': amount_rate,
                                'rate': partial.credit_move_id.move_id.payment_id.os_currency_rate,
                                'amount_base': amount_base,
                                'porcentaje': partial.credit_move_id.move_id.payment_id.payment_method_line_id.payment_method_id.percentage,
                                'amount': amount_rate *
                                partial.credit_move_id.move_id.payment_id.payment_method_line_id.payment_method_id.percentage / 100,
                                'currency_id': partial.credit_currency_id.id,
                            }
                            if not move.env['account.payment.igtf'].search([
                                    ('move_igtf_id', '=', partial.credit_move_id.move_id.payment_id.move_payment_igtf.id
                                     )]):
                                move.env['account.payment.igtf'].create(vals)
                                move.account_igtf_ids = move.env['account.payment.igtf'].search([
                                    ('move_id', '=', move.id)])

    @api.constrains('amount_total', 'amount_residual')
    def associate_move_with_in_invoice_igtf(self):
        for move in self.filtered(lambda x: x.state == 'posted' and x.move_type in ('in_invoice', 'in_refund')):
            move.account_igtf_ids.unlink()
            account_gene = move.partner_id.property_account_payable_id.id
            for line in move.line_ids:
                if line.account_id.id == account_gene:
                    account_partial_obj = move.env['account.partial.reconcile'].search([
                        ('credit_move_id', '=', line.id)])
                    for partial in account_partial_obj:
                        amount_base = 0.0
                        amount_rate = 0.0
                        if partial.debit_move_id.move_id.payment_id.payment_method_line_id.payment_method_id.is_igtf:
                            if partial.debit_currency_id != move.company_id.currency_id:
                                amount_base += partial.amount
                                amount_rate += partial.debit_amount_currency *\
                                    partial.debit_move_id.move_id.payment_id.os_currency_rate
                            if partial.debit_currency_id.id == move.company_id.currency_id:
                                amount_base += partial.amount
                                amount_rate += partial.amount /\
                                    partial.debit_move_id.move_id.payment_id.os_currency_rate

                            vals = {
                                'move_id': move.id,
                                'move_igtf_id': partial.debit_move_id.payment_id.move_payment_igtf.id,
                                'payment_method_id': partial.debit_move_id.move_id.payment_id.payment_method_line_id.payment_method_id.id,
                                'amount_rate': amount_rate,
                                'rate': partial.debit_move_id.move_id.payment_id.os_currency_rate,
                                'amount_base': amount_base,
                                'porcentaje': partial.debit_move_id.move_id.payment_id.payment_method_line_id.payment_method_id.percentage,
                                'amount': amount_rate *
                                partial.debit_move_id.move_id.payment_id.payment_method_line_id.payment_method_id.percentage / 100,
                                'currency_id': partial.debit_currency_id.id,
                            }
                            if not move.env['account.payment.igtf'].search([
                                    ('move_igtf_id', '=', partial.debit_move_id.move_id.payment_id.move_payment_igtf.id)
                            ]):
                                move.env['account.payment.igtf'].create(vals)
                                move.account_igtf_ids = move.env['account.payment.igtf'].search([
                                    ('move_id', '=', move.id)])
