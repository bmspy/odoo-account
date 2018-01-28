import logging
_logger = logging.getLogger(__name__)
from odoo import api, fields, models

class MoneyTransfersConfig(models.TransientModel):
    _name = 'money_transfers.config.settings'
    _inherit = 'res.config.settings'

    in_account_debit = fields.Many2one('account.account', 'Debit Account', domain=[('deprecated', '=', False)])
    in_account_credit = fields.Many2one('account.account', 'Credit Account', domain=[('deprecated', '=', False)])


    out_account_debit = fields.Many2one('account.account', 'Debit Account', domain=[('deprecated', '=', False)])
    out_account_credit = fields.Many2one('account.account', 'Credit Account', domain=[('deprecated', '=', False)])



    journal_id = fields.Many2one('account.journal', string='Payment Journal', required=True, domain=[('type', 'in', ('bank', 'cash'))])

    @api.multi
    def set_transfer_account_id(self):
        return self.env['ir.values'].sudo().set_default(
            'money_transfers.config.settings', 'journal_id', self.journal_id.id),
    @api.multi
    def set_transfer_account_id2(self):
        return self.env['ir.values'].sudo().set_default(
            'money_transfers.config.settings', 'in_account_debit', self.in_account_debit.id),
    @api.multi
    def set_transfer_account_id3(self):
        return self.env['ir.values'].sudo().set_default(
            'money_transfers.config.settings', 'out_account_debit', self.out_account_debit.id),
    @api.multi
    def set_transfer_account_id4(self):
        return self.env['ir.values'].sudo().set_default(
            'money_transfers.config.settings', 'in_account_credit', self.in_account_credit.id),
    @api.multi
    def set_transfer_account_id5(self):
        return self.env['ir.values'].sudo().set_default(
            'money_transfers.config.settings', 'out_account_credit', self.out_account_credit.id),
