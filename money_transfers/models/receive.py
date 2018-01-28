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

_logger = logging.getLogger(__name__)


class MoneyReceives(models.Model):
    _name = 'money_transfers_receive'
    _inherits = {'money_transfers': 'partner_recipient'}
    
    @api.one
    def _calcculatories(self):
        x =  str(self.partner_recipient.name)
        self.name = x

    name = fields.Char(compute="_calcculatories")#compute="_calcculatories")
    partner_recipient = fields.Many2one('money_transfers', string='Transfers ID')
    receive_amount = fields.Monetary(string='Received Amount')

    r_payment_date = fields.Date(string='Payment Date', default=fields.Date.context_today, required=True, copy=False)
    r_company_id = fields.Many2one('res.company', related='journal_id.company_id', string='Company', readonly=True)
    r_partner_id = fields.Many2one('res.partner','Customer', default=lambda self: self.env.user.partner_id)

    _sql_constraints = [
        ('partner_recipient_uniq', 'unique (partner_recipient)', "Transfers ID already exists !"),
        ('name_uniq', 'unique (name)', "Transfers ID already exists !")
    ]

    state_fileds = fields.Selection([
    	('draft', 'Draft'),
        ('validate', 'Validate'),
        ('pickup', 'PickUp'),
        ('pay', 'pay'),],
        default='draft') 
    
    @api.one
    def started_progress(self):
        if self.state != 'pay':
            raise UserError(_('Transter state Is : %s') % (self.state))
        self.write({
            'state_fileds': 'validate'
            })

    @api.one
    def progress_progress(self):
        self.write({
            'state_fileds': 'pickup'
            })

    @api.one
    def pay_progress(self):
        if self.receive_amount != self.transfer_amount:
            raise UserError(_('Transter Amount Not Equal Received Amount'))
        for rec in self:
            rec.accounting_scenarios_receive()
        self.write({
            'state_fileds': 'pay'
            })
        self.write({
            'state': 'transferred'
            })



    @api.multi
    def accounting_scenarios_receive(self):
        precision = self.env['decimal.precision'].precision_get('Payroll')

        for record in self:
            line_ids = []
            debit_sum = 0.0
            credit_sum = 0.0
            date = record.r_payment_date
            name = _('Receive of %s') % (record.name)
            move_dict = {
                'narration': name,
                'ref': record.name,
                'journal_id': record.journal_id.id,
                'date': date,
            }
            amount = record.receive_amount
            if float_is_zero(amount, precision_digits=precision):
                continue
            r_debit_account_id = self.env['ir.values'].get_default('money_transfers.config.settings', 'out_account_debit')
            r_credit_account_id = self.env['ir.values'].get_default('money_transfers.config.settings', 'out_account_credit')
            if r_debit_account_id:
                debit_line = (0, 0, {
                    'name': record.name,
                    'partner_id': record.r_partner_id.id,
                    'account_id': r_debit_account_id,
                    'journal_id': record.journal_id.id,
                    'date': date,
                    'debit': amount > 0.0 and amount or 0.0,
                    'credit': amount < 0.0 and -amount or 0.0,
                })
                line_ids.append(debit_line)
                debit_sum += debit_line[2]['debit'] - debit_line[2]['credit']

            if r_credit_account_id:
                credit_line = (0, 0, {
                    'name': record.name,
                    'partner_id': record.r_partner_id.id,
                    'account_id': r_credit_account_id,
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
                