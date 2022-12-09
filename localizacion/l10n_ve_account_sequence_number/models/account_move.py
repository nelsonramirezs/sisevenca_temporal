# -*- coding: utf-8 -*-

import logging
from odoo import fields, models, api
_logger = logging.getLogger('__name__')


class AccountMove(models.Model):
    _inherit = 'account.move'

    invoice_number_next = fields.Char(string='Nro Invoice', copy=False, tracking=True)
    invoice_number_control = fields.Char(string='Nro Control', copy=False, tracking=True)
    invoice_number_unique = fields.Char(string='Nro Control Unique', copy=False, tracking=True)
    delivery_note_next_number = fields.Char(string='Nro. Nota de Entrega', copy=False, tracking=True)
    is_delivery_note = fields.Boolean(default=False, tracking=True)
    is_control_unique = fields.Boolean(related='company_id.is_control_unique')
    is_manual = fields.Boolean(string='Numeracion Manual', tracking=True)
    hide_book = fields.Boolean(string='Excluir de Libros', tracking=True, default=False)
    reason = fields.Char('Referencia de Factura')
    is_branch_office = fields.Boolean(string='Tiene sucursal', tracking=True)

    @api.onchange('move_type')
    def _onchange_default_manual(self):
        if self.move_type in ['in_invoice', 'in_refund']:
            self.is_manual = True

    @api.onchange('is_delivery_note')
    def _onchange_hide_books(self):
        if self.is_delivery_note:
            self.hide_book = True
        else:
            self.hide_book = False

    def action_post(self):
        res = super(AccountMove, self).action_post()
        if self.is_delivery_note and not self.delivery_note_next_number:
            self.delivery_note_next_number = self.get_nro_nota_entrega()
        else:
            self.invoice_number_seq()
            self.invoice_control()
            self.invoice_number_control_unique()
        return res

    def invoice_number_seq(self):
        if not self.is_manual or not self.is_branch_office:
            if self.move_type in ['out_invoice'] and not self.debit_origin_id and not self.invoice_number_next:
                self.invoice_number_next = self.get_invoice_number()
            if self.move_type in ['out_refund'] and not self.invoice_number_next:
                self.invoice_number_next = self.get_refund_number()
            if self.move_type in ['out_invoice'] and self.debit_origin_id and not self.invoice_number_next:
                self.invoice_number_next = self.get_receipt_number()

    def invoice_control(self):
        if not self.is_control_unique or not self.is_manual or not self.is_branch_office:
            if self.move_type in ['out_invoice'] and not self.debit_origin_id and not self.invoice_number_control:
                self.invoice_number_control = self.get_invoice_number_control()
            if self.move_type in ['out_refund'] and not self.invoice_number_control:
                self.invoice_number_control = self.get_refund_number_control()
            if self.move_type in ['out_invoice'] and self.debit_origin_id and not self.invoice_number_control:
                self.invoice_number_control = self.get_receipt_number_control()

    def invoice_number_control_unique(self):
        if self.is_control_unique and not self.is_manual or not self.is_branch_office:
            if self.move_type in ['out_invoice'] and not self.debit_origin_id and not self.invoice_number_unique:
                self.invoice_number_unique = self.get_number_control_unique()
            if self.move_type in ['out_refund'] and not self.invoice_number_unique:
                self.invoice_number_unique = self.get_number_control_unique()
            if self.move_type in ['out_invoice'] and self.debit_origin_id and not self.invoice_number_unique:
                self.invoice_number_unique = self.get_number_control_unique()

    def get_invoice_number(self):
        self.ensure_one()
        if not self.is_delivery_note:
            seq = self.env['ir.sequence'].get('account.out.invoice')
            return seq
        return ''

    def get_invoice_number_control(self):
        self.ensure_one()
        if not self.is_delivery_note:
            seq = self.env['ir.sequence'].get('account.out.invoice.control')
            return seq
        return ''

    def get_refund_number(self):
        self.ensure_one()
        if not self.is_delivery_note:
            seq = self.env['ir.sequence'].get('account.credit.note')
            return seq
        return ''

    def get_refund_number_control(self):
        self.ensure_one()
        if not self.is_delivery_note:
            seq = self.env['ir.sequence'].get('account.credit.note.control')
            return seq
        return ''

    def get_receipt_number(self):
        self.ensure_one()
        if not self.is_delivery_note:
            seq = self.env['ir.sequence'].get('account.debit.note.cli')
            return seq
        return ''

    def get_receipt_number_control(self):
        self.ensure_one()
        if not self.is_delivery_note:
            seq = self.env['ir.sequence'].get('account.debit.note.control')
            return seq
        return ''

    def get_number_control_unique(self):
        self.ensure_one()
        if not self.is_delivery_note:
            seq = self.env['ir.sequence'].get('account.control.unique')
            return seq
        return ''

    def get_nro_nota_entrega(self):
        self.ensure_one()
        seq = self.env['ir.sequence'].get('account.delivery.note.sequence')
        return seq
