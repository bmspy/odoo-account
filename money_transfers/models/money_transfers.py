# -*- coding: utf-8 -*-

import json
from lxml import etree
from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.tools import float_is_zero, float_compare
from odoo.tools.misc import formatLang

from odoo.exceptions import UserError, RedirectWarning, ValidationError

import odoo.addons.decimal_precision as dp
import logging
import requests
import random


_logger = logging.getLogger(__name__)


class MoneyTransfers(models.Model):
    _name = 'money_transfers'

    partner_sender =  fields.Many2one('res.partner',string='Sender',required=True )

    sender_name = fields.Char(string='Name',
                               related='partner_sender.name')
    sender_phone = fields.Char(string='Phone',
                               related='partner_sender.phone')
    sender_email = fields.Char(string='Email',
                               related='partner_sender.email')
    sender_id = fields.Char(string='ID Number',
                               related='partner_sender.mobile')
    sender_adress = fields.Char(string='Address',
                               related='partner_sender.street')

    sender_type = fields.Char(string='Category',
                               related='partner_sender.website')


    def default_value(self):
        journal_default_value = self.env['ir.values'].get_default('money_transfers.config.settings', 'journal_id')
        return journal_default_value

    def default_randint_value(self):
        randint_value = "%0.6d" % random.randint(0,999999)
        return randint_value

    journal_id = fields.Many2one('account.journal', string='Payment Journal',default=default_value, required=True, domain=[('type', 'in', ('bank', 'cash'))])
    name = fields.Char(readonly=True , default=lambda x: str('New')) #default=default_randint_value
    #new fileds
    transfer_type = fields.Many2one('money_transfers.type','Transfer Type', required=True)
    commission_type = fields.Many2one('money_transfers.commission','Commission Type', required=True)

 

 #   destination_account_id = fields.Many2one('account.account')
   # partner_type = fields.Selection([('customer', 'Customer'), ('supplier', 'Vendor')])
   # partner_id = fields.Many2one('res.partner', string='Partner')
    partner_id = fields.Many2one('res.partner','Customer', default=lambda self: self.env.user.partner_id)

    payment_date = fields.Date(string='Payment Date', default=fields.Date.context_today, required=True, copy=False)
    company_id = fields.Many2one('res.company', related='journal_id.company_id', string='Company', readonly=True)
   # destination_journal_id = fields.Many2one('account.journal', string='Transfer To', domain=[('type', 'in', ('bank', 'cash'))])
   # payment_type = fields.Selection([('inbound', 'Inbound'), ('outbound', 'Outbound')], required=True)
  
    account_debit = fields.Many2one('account.account', 'Debit Account', domain=[('deprecated', '=', False)])
    account_credit = fields.Many2one('account.account', 'Credit Account', domain=[('deprecated', '=', False)])

    country_id = fields.Many2one('res.country', 'Country')
    _defaults = { 'country': lambda self, cr, uid, context: self.pool.get('res.country').browse(cr, uid, self.pool.get('res.country').search(cr, uid, [('code','=','GB')]))[0].id, } 


 
    @api.model
    def create(self, vals):
    	randint_value = str("%0.4d" % random.randint(0,9999))
        if not vals.get('name'):
            vals['name'] = randint_value + self.env['ir.sequence'].next_by_code('money_transfers') or str('New')
        transref = super(MoneyTransfers, self).create(vals)
        return transref


    partner_recipient = fields.Many2one('res.partner', string='Receiver',required=True)

    receiver_name = fields.Char(string='Name',
                               related='partner_recipient.name')
    receiver_phone = fields.Char(string='Phone',
                               related='partner_recipient.phone')
    receiver_email = fields.Char(string='Email',
                               related='partner_recipient.email')
    receiver_id = fields.Char(string='ID Number',
                               related='partner_recipient.mobile')
    receiver_adress = fields.Char(string='Address',
                               related='partner_recipient.street')

    receiver_type = fields.Char(string='Category',
                               related='partner_recipient.website')




    ser6_partner_id = fields.Many2one('res.partner', string='Customer')# , default=_get_default_partner)
    currency_id = fields.Many2one('res.currency', string='Currency',
                              default=lambda self: self.env.user.company_id.currency_id)
    transfers_reason = fields.Many2one('money_transfers.reason','Reason of transfer')


    send_currency_id = fields.Many2one('res.currency', string='Currency',
                              default=lambda self: self.env.user.company_id.currency_id)

    receive_currency_id = fields.Many2one('res.currency', string='Currency',
                              default=lambda self: self.env.user.company_id.currency_id)


    transfer_amount = fields.Monetary(string='Amount')
    transfer_commission = fields.Float(string='Commission')
 
 


    receive_country_id = fields.Many2one('res.country', 'Country')

    @api.one
    def _calcculatstransfer_amount(self):
        self.stransfer_amount = self.transfer_amount

    stransfer_amount = fields.Monetary(compute="_calcculatstransfer_amount", string='Amount')


    @api.one
    def _calcculatstransfer_commission(self):
        self.stransfer_commission = self.transfer_commission

    stransfer_commission = fields.Monetary(compute="_calcculatstransfer_commission", string='Commission')



    @api.one
    def _calcculatories(self):
        self.total_amount = self.stransfer_amount + self.stransfer_commission


    total_amount = fields.Monetary(compute="_calcculatories", string='Total Amount')
 
 

    state = fields.Selection([
        ('draft', 'Draft'),
        ('validate', 'Validate'),
        ('pay', 'Paid'),
        ('transferred', 'Transferred'),],
        default='draft') 
      #  ('concept', 'Validate'),
       # ('started', 'Paid'),
        #('progress', 'Transferred'),
        #('finished', 'Done'),],
        #default='concept') 
    

  #  @api.one
  #  def concept_progressbar(self):
   #     self.write({
    #        'state': 'concept',
     #       })
    @api.one
    def validate_progressbar(self):
        self.write({
            'state': 'validate'
            })




    @api.multi
    def pay_progressbar(self):
        for rec in self:

            if rec.state != 'validate':
                raise UserError(_("Only a pay payment can be posted. Trying to post a payment in state %s.") % rec.state)
 
            sequence_code = self.name
            amount =  rec.transfer_amount 
           # rec.accounting_scenarios()
            transfer_debit_aml = rec.accounting_scenarios()
            rec.write({'state': 'pay'})


 

 
    @api.one
    def transferred_progressbar(self):
        self.write({
            'state': 'transferred'
            })



    


 

    @api.multi
    def accounting_scenarios(self):
        precision = self.env['decimal.precision'].precision_get('Payroll')

        for record in self:
            line_ids = []
            debit_sum = 0.0
            credit_sum = 0.0
            date = record.payment_date
            name = _('Transfer of %s') % (record.name)
            move_dict = {
                'narration': name,
                'ref': record.name,
                'journal_id': record.journal_id.id,
                'date': date,
            }
            amount = record.transfer_amount
            if float_is_zero(amount, precision_digits=precision):
                continue
            debit_account_id = self.env['ir.values'].get_default('money_transfers.config.settings', 'in_account_debit')
            credit_account_id = self.env['ir.values'].get_default('money_transfers.config.settings', 'in_account_credit')
            if debit_account_id:
                debit_line = (0, 0, {
                    'name': record.name,
                    'partner_id': record.partner_id.id,
                    'account_id': debit_account_id,
                    'journal_id': record.journal_id.id,
                    'date': date,
                    'debit': amount > 0.0 and amount or 0.0,
                    'credit': amount < 0.0 and -amount or 0.0,
                })
                line_ids.append(debit_line)
                debit_sum += debit_line[2]['debit'] - debit_line[2]['credit']

            if credit_account_id:
                credit_line = (0, 0, {
                    'name': record.name,
                    'partner_id': record.partner_id.id,
                    'account_id': credit_account_id,
                    'journal_id': record.journal_id.id,
                    'date': date,
                    'debit': amount < 0.0 and -amount or 0.0,
                    'credit': amount > 0.0 and amount or 0.0,
                })
                line_ids.append(credit_line)
                credit_sum += credit_line[2]['credit'] - credit_line[2]['debit']

            if float_compare(credit_sum, debit_sum, precision_digits=precision) == -1:
                acc_id = record.journal_id.default_credit_account_id.id
                if not acc_id:
                    raise UserError(_('Transfer Journal "%s" has not properly configured the Credit Account!') % (record.journal_id.name))
                adjust_credit = (0, 0, {
                    'name': _('Adjustment Entry'),
                    'partner_id': False,
                    'account_id': acc_id,
                    'journal_id': record.journal_id.id,
                    'date': date,
                    'debit': 0.0,
                    'credit': debit_sum - credit_sum,
                })
                line_ids.append(adjust_credit)

            elif float_compare(debit_sum, credit_sum, precision_digits=precision) == -1:
                acc_id = record.journal_id.default_debit_account_id.id
                if not acc_id:
                    raise UserError(_('Transfer Journal "%s" has not properly configured the Debit Account!') % (record.journal_id.name))
                adjust_debit = (0, 0, {
                    'name': _('Adjustment Entry'),
                    'partner_id': False,
                    'account_id': acc_id,
                    'journal_id': record.journal_id.id,
                    'date': date,
                    'debit': credit_sum - debit_sum,
                    'credit': 0.0,
                })
                line_ids.append(adjust_debit)
            move_dict['line_ids'] = line_ids
            move = self.env['account.move'].create(move_dict)
            record.write({'move_id': move.id, 'date': date})
            move.post()
                


class MoneyTransfersType(models.Model):
    _name = 'money_transfers.type'
    _description = "Papers Type"
    name = fields.Char('The Type', required=True, translate=True)
    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Type name already exists !"),
    ]
class MoneyTransfersTypecommission(models.Model):
    _name = 'money_transfers.commission'
    _description = "Commission Type"
    name = fields.Char('The Type', required=True, translate=True)
    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Type name already exists !"),
    ]

class MoneyTransfersReason(models.Model):
    _name = 'money_transfers.reason'
    _description = "Reason Transfers"
    name = fields.Char('Reason Transfers', required=True, translate=True)
    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Reason Transfers already exists !"),
    ]

class MoneyTransfersPercentage(models.Model):
    _name = 'money_transfers.percentage'
    _description = "Percentage payment"
    name = fields.Float('Percentage payment', required=True, translate=True)
    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Percentage payment already exists !"),
    ]
