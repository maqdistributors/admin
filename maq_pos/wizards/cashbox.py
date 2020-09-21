# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError

coin_values = [0.05, 0.10, 0.25, 1.00, 2.00, 5.00, 10.00, 20.00, 50.00, 100.00]


class AccountCashboxLine(models.Model):
    _inherit = 'account.cashbox.line'

    cashbox_in_id = fields.Many2one('custom.cash.box.in', string="Cashbox In")
    cashbox_out_id = fields.Many2one('custom.cash.box.out', string="Cashbox Out")
    cashbox_out_id = fields.Many2one('custom.cash.box.out', string="Cashbox Out")


class CustomCashBoxIn(models.Model):
    _name = 'custom.cash.box.in'
    _description = "Custom Cash Box In"

    @api.depends('cashbox_lines_ids.subtotal')
    def _cal_total(self):
        """
        Compute the total amounts of the SO.
        """
        for record in self:
            total = 0.0
            for line in record.cashbox_lines_ids:
                total += line.subtotal or 0
            if total <= 0:
                raise UserError(
                    _("Please enter number of coins. Total should not be 0 or less than 0."))

            record.update({
                'put_money_in': total,
            })

    @api.model
    def default_get(self, fields):
        """
        Set default cash values combination in Cashboxline
        """
        vals = super(CustomCashBoxIn, self).default_get(fields)
        vals['cashbox_lines_ids'] = [
            [0, 0, {'coin_value': cv, 'number': 0, 'subtotal': 0}] for cv in coin_values]
        return vals

    cashbox_lines_ids = fields.One2many(
        'account.cashbox.line', 'cashbox_in_id', string='Cashbox Lines')
    ref = fields.Char('Reference')
    pos_session_id = fields.Many2one('pos.session', string="POS Session")
    put_money_in = fields.Float(
        string='Total', store=True, readonly=True, compute='_cal_total')

    @api.multi
    def run(self):
        for record in self:
            active_model = record.env.context.get('active_model', False)
            active_ids = record.env.context.get('active_ids', [])

            total = 0.0
            for line in record.cashbox_lines_ids:
                total += line.subtotal

            for active_id in active_ids:
                if active_model == 'pos.session':
                    pos_session_ids = self.env[active_model].browse(active_id)
                    bank_statements = [
                        session.cash_register_id for session in pos_session_ids if session.cash_register_id]
                    if not bank_statements:
                        raise UserError(
                            _("There is no cash register for this PoS Session"))
                    bank_statements = bank_statements[0]
                    if not bank_statements.journal_id.company_id.transfer_account_id:
                        raise UserError(
                            _("You should have defined an 'Internal Transfer Account' in your cash register's journal!"))
                    values = {
                        'date': bank_statements.date,
                        'statement_id': bank_statements.id,
                        'journal_id': bank_statements.journal_id.id,
                        'amount': total,
                        'account_id': bank_statements.journal_id.company_id.transfer_account_id.id,
                        'ref': '%s' % (self.ref or ''),
                        'name': pos_session_ids.name,
                    }
                    bank_statements.write({'line_ids': [(0, False, values)]})
                    record.update({'pos_session_id': active_id})


class CustomCashBoxOut(models.Model):
    _name = 'custom.cash.box.out'
    _description = "Custom Cash Box Out"

    @api.depends('cashbox_lines_ids.subtotal')
    def _cal_total(self):
        """
        Compute the total amounts of the SO.
        """
        for record in self:
            total = 0.0
            for line in record.cashbox_lines_ids:
                total += line.subtotal
            if total <= 0:
                raise UserError(
                    _("Please enter number of coins. Total should not be 0 or less than 0."))
            record.update({
                'put_money_out': total,
            })

    @api.model
    def default_get(self, fields):
        """
        Set default cash values combination in Cashboxline
        """
        vals = super(CustomCashBoxOut, self).default_get(fields)
        vals['cashbox_lines_ids'] = [
            [0, 0, {'coin_value': cv, 'number': 0, 'subtotal': 0}] for cv in coin_values]
        return vals

    cashbox_lines_ids = fields.One2many(
        'account.cashbox.line', 'cashbox_out_id', string='Cashbox Lines')
    ref = fields.Char('Reference')
    pos_session_id = fields.Many2one('pos.session', string="POS Session")
    put_money_out = fields.Float(
        string='Total', store=True, readonly=True, compute='_cal_total')

    @api.multi
    def run(self):
        for record in self:
            active_model = record.env.context.get('active_model', False)
            active_ids = record.env.context.get('active_ids', [])

            total = 0.0
            for line in record.cashbox_lines_ids:
                total += line.subtotal

            for active_id in active_ids:
                if active_model == 'pos.session':
                    pos_session_ids = self.env[active_model].browse(active_id)
                    bank_statements = [
                        session.cash_register_id for session in pos_session_ids if session.cash_register_id]
                    if not bank_statements:
                        raise UserError(
                            _("There is no cash register for this PoS Session"))
                    bank_statements = bank_statements[0]
                    if not bank_statements.journal_id.company_id.transfer_account_id:
                        raise UserError(
                            _("You should have defined an 'Internal Transfer Account' in your cash register's journal!"))
                    values = {
                        'date': bank_statements.date,
                        'statement_id': bank_statements.id,
                        'journal_id': bank_statements.journal_id.id,
                        'amount': -total if total > 0.0 else total,
                        'account_id': bank_statements.journal_id.company_id.transfer_account_id.id,
                        'ref': '%s' % (self.ref or ''),
                        'name': pos_session_ids.name,
                    }
                    bank_statements.write({'line_ids': [(0, False, values)]})
                    record.update({'pos_session_id': active_id})


class POSSession(models.Model):
    _inherit = 'pos.session'

    m_cashbox_out_ids = fields.One2many(
        'custom.cash.box.out', 'pos_session_id', string='Cashbox Lines')
    m_cashbox_in_ids = fields.One2many(
        'custom.cash.box.in', 'pos_session_id', string='Cashbox Lines')
