from datetime import datetime, timedelta
from odoo import models, fields


class ResumeIgtfWizard(models.TransientModel):
    _name = "resume.igtf.wizard"

    type_business = fields.Selection([('supplier', 'Proveedor'), ('customer', 'Cliente')], string="Tipo de Empresa",
                                     default='customer')
    type_payment = fields.Selection([('payment_fact', 'Incluyendo Facturas'),
                                     ('payment', 'Sin incluir Facturas')], string="Tipo de Pago",
                                    default='payment_fact')
    date_from = fields.Date(default=lambda *a: (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'),
                            string="Desde")
    date_to = fields.Date(default=lambda *a: datetime.now().strftime('%Y-%m-%d'), string="Hasta")
    date_today = fields.Date(default=lambda *a: datetime.now().strftime('%Y-%m-%d'))
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id.id)

    def get_payment(self):
        cursor = self.env['account.payment'].search(
            [('date', '>=', self.date_from), ('date', '<=', self.date_to), ('partner_type', '=', self.type_business)],
            order='date asc')
        lines = []
        for rec in cursor:
            vals = {}
            rate = (rec.move_id.amount_total_signed / rec.move_id.amount_total)
            if rec.move_payment_igtf:
                vals.update({
                    'move_id': rec.move_payment_igtf.id,
                    'payment_method_id': rec.payment_method_line_id.payment_method_id.id,
                    'amount_base_usd': rec.amount,
                    'rate': rec.move_id.amount_total_signed / rec.move_id.amount_total,
                    'amount_base': rec.amount * rate,
                    'percentage': rec.payment_method_id.percentage,
                    'amount_ret': rec.move_payment_igtf.amount_total_signed,
                    'type_igtf': "Pag. En Divisas",
                    'journal_id': rec.journal_id.id,
                    'payment_id': rec.id,
                })
            if rec.move_provider_igtf:
                vals.update({
                    'move_id': rec.move_provider_igtf,
                    'payment_method_id': rec.payment_method_line_id.payment_method_id,
                    'amount_base_usd': rec.amount if rec.currency_id != self.env.company.currency_id.id else 0.0,
                    'rate': rate,
                    'amount_base': rec.amount * rate,
                    'percentage': rec.journal_id.percentage,
                    'amount_ret': rec.move_provider_igtf.amount_total_signed,
                    'type_igtf': "Pag. por Bancos",
                    'journal_id': rec.journal_id,
                    'payment_id': rec.id,
                })
            lines.append(vals)
        print(lines)
        return lines

    def get_invoice(self):
        lines = []
        move_type = ('out_invoice', 'out_refund', 'out_receipt') if self.type_business == 'customer'\
            else ('in_invoice', 'in_refund', 'in_receipt')

        cursor_resumen = self.env['account.payment.igtf'].search([('move_id.invoice_date', '>=', self.date_from),
                                                                  ('move_id.invoice_date', '<=', self.date_to),
                                                                  ('move_id.state', '=', 'posted'),
                                                                  ('move_id.company_id', '=', self.company_id.id),
                                                                  ('move_id.move_type', 'in', move_type),
                                                                  ])
        for det in cursor_resumen:
            vals = {
                'move_id': det.move_id,
                'move_igtf_id': det.move_igtf_id,
                'payment_method_id': det.payment_method_id,
                'amount_base_usd': det.amount_rate,
                'rate': det.rate,
                'monto_base': det.amount_base,
                'porcentaje': det.porcentaje,
                'amount': det.amount,
            }
            lines.append(vals)
        print(lines)
        return lines

    def print_report_resume_invoice_igft(self):
        return self.env.ref('l10n_ve_igtf.action_resume_invoice_igtf_report').report_action(self)

    def print_report_resume_payment_igft(self):
        return self.env.ref('l10n_ve_igtf.action_iva_retention_resume_report').report_action(self)
