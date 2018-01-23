
from odoo import api, models , fields
import odoo.addons.decimal_precision as dp



class Exchange_pairs(models.Model):
    _name = 'exchange.pairs'
    _description = 'this Module For Handle your Exchange Currencies'
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    name       = fields.Char("Currency pairs" , track_visibility='onchange')

    currency_id = fields.Many2one('res.currency', string='Currency')

    c1  = fields.Many2one('res.currency' ,string='Currency 1', currency_field='currency_id' , track_visibility='always', required=True, default=lambda self: self.env.user.company_id.currency_id)
    c2  = fields.Many2one('res.currency' ,string='Currency 2', currency_field='currency_id' , track_visibility='always', required=True, default=lambda self: self.env.user.company_id.currency_id)


    @api.onchange('c2','c1')
    def _get_value_sell(self):
        if self.c2:
            self.name    = str(str(self.c1.name) + " / " + str(self.c2.name))