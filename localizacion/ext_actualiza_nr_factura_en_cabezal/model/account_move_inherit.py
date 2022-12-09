# -*- coding: utf-8 -*-


import logging
from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError




class AccountMOve(models.Model):
    _inherit = 'account.move'

    def action_post(self):
        super().action_post()
        self.actualiza_name_nota()

    @api.onchange('state')
    def actualiza_name_nota(self):
        if self.state=='posted':
            if self.is_delivery_note!=True:
                if self.invoice_number_next!=False:
                    self.name=str(self.invoice_number_next)
                    self.payment_reference=str(self.invoice_number_next)
                    self.sequence_prefix=str(self.invoice_number_next)
            else:
                if self.delivery_note_next_number:
                    self.name=str(self.delivery_note_next_number)
                    self.payment_reference=str(self.delivery_note_next_number)
                    self.sequence_prefix=str(self.delivery_note_next_number)
