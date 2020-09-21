# -*- coding: utf-8 -*-

from odoo import api, fields, models


class AccountCashboxLine(models.Model):
    _inherit = 'account.cashbox.line'

    m_cashbox_summary_id = fields.Many2one(
        'account.cashbox.summary', string="Cashbox Summary Id")


class AccountCashboxSummary(models.Model):
    """ Cash Box Summary """
    _name = 'account.cashbox.summary'
    _description = 'CashBox Summary'

    @api.depends('cashbox_lines_ids.subtotal')
    def _cal_total(self):
        """
        Compute the total amounts of the SO.
        """
        for record in self:
            total = 0.0
            for line in record.cashbox_lines_ids:
                total += line.subtotal
            record.update({'total': total, })

    cashbox_lines_ids = fields.One2many(
        'account.cashbox.line', 'm_cashbox_summary_id', string='Cashbox Lines')
    pos_session_id = fields.Many2one('pos.session', string="POS Session")
    balance_type = fields.Selection([('start', 'Start'), ('end', 'End'), ('other', 'Other')], default='other')
    total = fields.Float(string='Total', store=True,
                         readonly=True, compute='_cal_total')


class POSSession(models.Model):
    _inherit = 'pos.session'

    m_cashbox_summary_ids = fields.One2many(
        'account.cashbox.summary', 'pos_session_id', string='Cashbox Lines')

    @api.multi
    def open_cashbox(self):
        vals = super(POSSession, self).open_cashbox()
        if vals.get('context'):
            vals['context'].update({'pos_session_id': self.id})
        return vals


class AccountBankStmtCashWizard(models.Model):
    _inherit = 'account.bank.statement.cashbox'

    @api.multi
    def validate(self):
        bnk_stmt_id = self.env.context.get(
            'bank_statement_id', False) or self.env.context.get('active_id', False)
        bnk_stmt = self.env['account.bank.statement'].browse(bnk_stmt_id)
        total = 0.0
        for lines in self.cashbox_lines_ids:
            total += lines.subtotal
        if self.env.context.get('balance', False) == 'start':
            # starting balance
            bnk_stmt.write(
                {'balance_start': total, 'cashbox_start_id': self.id})
        else:
            # closing balance
            bnk_stmt.write({'balance_end_real': total,
                            'cashbox_end_id': self.id})

        pos_session_id = self.env.context.get('pos_session_id', False)
        if pos_session_id:
            cash_box_data = []
            for cash_box in self.cashbox_lines_ids.read():
                data = (0, 0, {'coin_value': cash_box.get('coin_value'), 'number': cash_box.get(
                    'number'), 'subtotal': cash_box.get('subtotal')})
                cash_box_data.append(data)

            if cash_box_data:
                balance_type = self.env.context.get('balance', 'other')

                self.env['account.cashbox.summary'].create(
                    {'balance_type':balance_type, 'pos_session_id': pos_session_id, 'cashbox_lines_ids': cash_box_data})

        return {'type': 'ir.actions.act_window_close'}
