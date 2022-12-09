# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    cost_usd = fields.Float(string='Coste $', compute='_compute_cost_rate',
                            inverse='_set_cost_rate', search='_search_cost_rate')
    os_currency_rate = fields.Float(string='Tipo de Cambio', default=lambda x: x.env['res.currency.rate'].search(
        [('name', '<=', fields.Date.today()), ('currency_id', '=', 2)], limit=1).sell_rate, digits=(12, 2),
                                    readonly=True)

    def _prepare_variant_values(self, combination):
        res = super(ProductTemplate, self)._prepare_variant_values(combination)
        res.update({
            'os_currency_rate': self.os_currency_rate
        })
        return res

    @api.onchange('standard_price')
    @api.constrains('standard_price')
    def _check_rate_cost_usd(self):
        for product in self:
            if product.standard_price > 0.0 and product.os_currency_rate:
                rate = product.standard_price / product.os_currency_rate
                product.cost_usd = rate

    @api.onchange('cost_usd')
    @api.constrains('cost_usd')
    def _check_rate_cost_bs(self):
        for product in self:
            if product.cost_usd > 0.0 and product.os_currency_rate:
                rate = product.cost_usd * product.os_currency_rate
                product.standard_price = rate

    def _search_cost_rate(self, operator, value):
        products = self.env['product.product'].search([('cost_usd', operator, value)], limit=None)
        return [('id', 'in', products.mapped('product_tmpl_id').ids)]

    def _set_cost_rate(self):
        for template in self:
            if len(template.product_variant_ids) == 1:
                template.product_variant_ids.cost_usd = template.cost_usd

    @api.depends_context('company')
    @api.depends('product_variant_ids', 'product_variant_ids.cost_usd')
    def _compute_cost_rate(self):
        # Depends on force_company context because standard_price is company_dependent
        # on the product_product
        unique_variants = self.filtered(lambda template: len(template.product_variant_ids) == 1)
        for template in unique_variants:
            template.cost_usd = template.product_variant_ids.cost_usd
        for template in (self - unique_variants):
            template.cost_usd = 0.0
