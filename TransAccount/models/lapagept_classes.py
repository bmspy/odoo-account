from odoo import api, models , fields

class Transbe(models.Model):
    _name = "account.journal"
    _inherit = 'account.move'

    x_myDescription = fields.Char('Description', required=True, default='Description here ...')
    x_myDebitCredit = fields.Char('Debit/Kredit', required=True, default='D')
    x_myPartner = fields.Many2one('res.partner', 'Customer')
    x_myAccount = fields.Many2one('account.account', 'Account')


