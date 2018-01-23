from odoo import api, models , fields
import odoo.addons.decimal_precision as dp



class Exchange_Currencies(models.Model):
    _name = 'exchange.currencies'
    _description = 'this Module For Handle your Exchange Currencies'
    _inherit = ['mail.thread', 'ir.needaction_mixin']


    time        = fields.Datetime('Current Time', readonly=True, select=True, default=lambda self: fields.datetime.now())
    c_name      = fields.Char(string="Name")

    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.user.company_id.currency_id)
    currency_id_2 = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.user.company_id.currency_id)

    trans_amount = fields.Monetary(string='Amount')

    pairs_t     = fields.Many2one("exchange.rate" ,track_visibility='always')

    c1 =   fields.Many2one( related='pairs_t.c1' , readonly=True ,currency_field='currency_id')
    c2 =   fields.Many2one( related='pairs_t.c2' , readonly=True ,currency_field='currency_id_2' )



    selling_price = fields.Float(string='price', related='pairs_t.selling_price' , currency_field='currency_id')

    buy_price = fields.Float(string='buy_price', related='pairs_t.buy_price' , currency_field='currency_id_2')

    type_transaction = fields.Selection([('s', 'sell'), ('b', 'buy')], string='Type' , track_visibility='always')

    end_amount  =   fields.Float("End Amount" , readonly=True , track_visibility='always' , compute="_end_amount")

    trans_detal =   fields.Char("Transcation Details" , readonly=True , track_visibility='always' , compute="_trans_detal")



    @api.onchange('type_transaction' , 'pairs_t' , 'trans_amount')
    def _end_amount(self):
        if self.type_transaction == 's':
            self.currency_id = self.c1
            self.currency_id_2 = self.c2
            self.end_amount = (self.trans_amount * self.selling_price)
            Rate = self.selling_price
            global Rate
        elif self.type_transaction == 'b':
            self.currency_id = self.c2
            self.currency_id_2 = self.c1
            self.end_amount = (self.trans_amount / self.buy_price)
            Rate = self.buy_price
            global Rate




    @api.onchange('end_amount')
    def _trans_detal(self):
        if self.trans_amount:
            if self.type_transaction == 's':
                self.trans_detal    = str(str(self.trans_amount) + " x " + str(Rate))
            elif self.type_transaction == 'b':
                self.trans_detal    = str(str(self.trans_amount) + " / " + str(Rate))

