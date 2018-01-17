from odoo import api, models , fields



class BusinessTrip(models.Model):
    _name = 'transfer.base'
    _description = 'Business Trip'

    date        = fields.Date(required=True , index=True, default=fields.Date.context_today)

    move_id     = fields.Many2one('account.move', string='Journal Entry', ondelete="cascade",
                            help="The move of this entry line.", index=True, required=True, auto_join=True)

    journal_id  = fields.Many2one('account.journal', related='move_id.journal_id', string='Journal',
                            index=True, store=True, copy=False)  # related is required

    ref         = fields.Char(related='move_id.ref', string='Reference', store=True, copy=False, index=True)

    line_ids    = fields.One2many('account.move.line', 'move_id', string='Journal Items',
                               copy=True)

    sequence    = fields.Integer("account.bank.statement.line.sequence")