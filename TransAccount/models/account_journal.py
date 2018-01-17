from odoo import models, fields


class account_journal(models.Model):
    _inherit = "account.journal"

    allow_account_transfer = fields.Boolean(
        'Allow Account Transfer?',
        default=True,
        help='Set if this journals can be used on account transfers'
        )
