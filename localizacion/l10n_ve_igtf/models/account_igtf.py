# -*- coding: utf-8 -*-

from odoo import fields, models, api


class AccountIgtf(models.Model):
    _name = 'account.payment.igtf'
    _description = 'Igtf'

    move_id = fields.Many2one('account.move', string="Factura")
    move_igtf_id = fields.Many2one('account.move', string="Asiento contable igtf")
    payment_method_id = fields.Many2one('account.payment.method', string="Metodo de Pago")
    currency_id = fields.Many2one('res.currency', string='Moneda')
    rate = fields.Float(string="Tasa")
    porcentaje = fields.Float(string="Porcentaje")
    amount = fields.Float(string="Monto retenido")
    amount_rate = fields.Float()
    amount_base = fields.Float()
