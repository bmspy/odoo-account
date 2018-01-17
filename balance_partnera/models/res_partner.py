

from odoo import api, fields, models, _
import logging , time

_logger = logging.getLogger(__name__)



class ResPartner(models.Model):

    _inherit = "res.partner"


    debit = fields.Float('res.partner.debit')
    credit = fields.Float('res.partner.credit')


    journal_item_count = fields.Float('res.partner.journal_item_count')


    currency_id = fields.Many2one('res.currency', string='Currency')
    property_account_payable_id = fields.Many2one('res.partner.property_account_payable_id', string='Account Payable')
    property_account_receivable_id = fields.Many2one('res.partner.property_account_payable_id', string='Account Receivable')
    invoice_ids = fields.Many2one('res.partner.invoice_ids')
    issued_total = fields.Monetary('res.partner.issued_total')


    def _get_total_amount_invoice(self):
        res = {}
        for partner in self:
            invoice_obj = self.env['account.invoice']
            invoice_ids = invoice_obj.search([('partner_id', '=', partner.id)])
            amount_total = 0
            for invoice in invoice_ids:
                amount_total += invoice.amount_total
            res.update({'total_amount_invoice': amount_total})

    def _get_total_balance_invoice(self):
        res = {}
        for partner in self:
            invoice_obj = self.env['account.invoice']
            invoice_ids = invoice_obj.search([('partner_id', '=', partner.id)])
            balance_total = 0
            for invoice in invoice_ids:
                balance_total += invoice.residual
            res.update({'total_balance_invoice': balance_total})





    total_balance_invoice = fields.Monetary(string='Balance Total', type='float',
                                            readonly=True, currency_field='currency_id' , compute='_get_total_balance_invoice')
    total_amount_invoice = fields.Monetary(string='Amount Total', type='float',
                                   readonly=True, currency_field='currency_id', compute='_get_total_amount_invoice')