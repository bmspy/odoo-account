from odoo import api, models , fields
import odoo.addons.decimal_precision as dp



class Exchange_rate(models.Model):
    _name = 'exchange.rate'
    _description = 'this Module For Handle your Exchange Currencies'
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    time        = fields.Datetime('Current Time', readonly=True, select=True, default=lambda self: fields.datetime.now())

    name = fields.Many2one("exchange.pairs" ,track_visibility='always')
    c1   = fields.Many2one( related='name.c1')
    c2   = fields.Many2one( related='name.c2')

    selling_price    = fields.Float(track_visibility='always')
    buy_price        = fields.Float(track_visibility='always')


    @api.onchange('pairs')
    def _get_value_buy(self):
        if self.buy_price:
            self.result1    = str("From " + str(self.c1.name) + " To " + str(self.c2.name) + " = " + str(self.buy_price))

    @api.onchange('pairs')
    def _get_value_sell(self):
        if self.selling_price:
            self.result2    = str("From " + str(self.c2.name) + " To " + str(self.c1.name) + " = " + str(self.selling_price))