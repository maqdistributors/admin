# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class account_bank_reconciliation_report(models.AbstractModel):
    _inherit = "account.bank.reconciliation.report"

    @api.model
    def get_lines(self, options, line_id=None):
        """
        Overwrite a def get_lines function to make arrange a sequnce in Bank reconcilation report
        All the records will display in ascending order
        """
        journal_id = self._context.get('active_id') or options.get('active_id')
        journal = self.env['account.journal'].browse(journal_id)
        lines = []
        # Start amount
        use_foreign_currency = \
            journal.currency_id != journal.company_id.currency_id \
            if journal.currency_id else False
        account_ids = list(
            set([journal.default_debit_account_id.id, journal.default_credit_account_id.id]))
        line_currency = journal.currency_id if use_foreign_currency else False
        self = self.with_context(line_currency=line_currency)
        lines_already_accounted = self.env['account.move.line'].search(
            [
                ('account_id', 'in', account_ids),
                ('date', '<=', self.env.context['date_to']),
                ('company_id', 'in', self.env.context['company_ids'])
            ], order='date asc')
        start_amount = sum(
            [
                line.amount_currency if use_foreign_currency else line.balance
                for line in lines_already_accounted
            ])
        lines.append(self.add_title_line(options, _(
            "Current Balance in GL"), start_amount))

        # Un-reconcilied bank statement lines
        move_lines = self.env['account.move.line'].search(
            [
                ('move_id.journal_id', '=', journal_id),
                '|', ('statement_line_id', '=', False),
                ('statement_line_id.date', '>',
                 self.env.context['date_to']),
                ('user_type_id.type', '=', 'liquidity'),
                ('full_reconcile_id', '=', False),
                ('date', '<=', self.env.context['date_to']),
                ('company_id', 'in', self.env.context['company_ids'])
            ], order='date asc')

        unrec_tot = 0
        if move_lines:
            tmp_lines = []
            for line in move_lines:
                self.line_number += 1
                line_description = line_title = line.ref
                if line_description and len(line_description) > 83 and not self.env.context.get('print_mode'):
                    line_description = line.ref[:80] + '...'
                tmp_lines.append({
                    'id': str(line.id),
                    #'move_id': line.move_id.id,
                    #'type': 'move_line_id',
                    #'action': line.get_model_id_and_name(),
                    'name': line.name,
                    'columns': [
                        {'name': line.date},
                        {'name': line_description, 'title': line_title,
                            'class': 'whitespace_print'},
                        {'name': self.format_value(
                            -line.amount_currency if use_foreign_currency else -line.balance,
                            line_currency)
                         },
                    ],
                    'level': 1,
                })
                unrec_tot -= line.amount_currency if use_foreign_currency else line.balance
            if unrec_tot > 0:
                title = _("Plus Unreconciled Payments")
            else:
                title = _("Minus Unreconciled Payments")
            lines.append(self.add_subtitle_line(title))
            lines += tmp_lines
            lines.append(self.add_total_line(unrec_tot))

        # Outstanding plus
        not_reconcile_plus = self.env['account.bank.statement.line'].search(
            [
                ('statement_id.journal_id', '=', journal_id),
                ('date', '<=', self.env.context['date_to']),
                ('journal_entry_ids', '=', False),
                ('amount', '>', 0),
                ('company_id', 'in', self.env.context['company_ids'])])
        outstanding_plus_tot = 0
        if not_reconcile_plus:
            lines.append(self.add_subtitle_line(
                _("Plus Unreconciled Statement Lines")))
            for line in not_reconcile_plus:
                lines.append(self.add_bank_statement_line(line, line.amount))
                outstanding_plus_tot += line.amount
            lines.append(self.add_total_line(outstanding_plus_tot))

        # Outstanding less
        not_reconcile_less = self.env['account.bank.statement.line'].search(
            [
                ('statement_id.journal_id', '=', journal_id),
                ('date', '<=', self.env.context['date_to']),
                ('journal_entry_ids', '=', False),
                ('amount', '<', 0),
                ('company_id', 'in', self.env.context['company_ids'])])
        outstanding_less_tot = 0
        if not_reconcile_less:
            lines.append(self.add_subtitle_line(
                _("Minus Unreconciled Statement Lines")))
            for line in not_reconcile_less:
                lines.append(self.add_bank_statement_line(line, line.amount))
                outstanding_less_tot += line.amount
            lines.append(self.add_total_line(outstanding_less_tot))

        # Final
        computed_stmt_balance = start_amount + \
            outstanding_plus_tot + outstanding_less_tot + unrec_tot
        last_statement = self.env['account.bank.statement'].search(
            [
                ('journal_id', '=', journal_id),
                ('date', '<=', self.env.context['date_to']),
                ('company_id', 'in', self.env.context['company_ids'])
            ], order="date asc, id asc", limit=1)
        real_last_stmt_balance = last_statement.balance_end
        if computed_stmt_balance != real_last_stmt_balance:
            if real_last_stmt_balance - computed_stmt_balance > 0:
                title = _("Plus Missing Statements")
            else:
                title = _("Minus Missing Statements")
            lines.append(self.add_subtitle_line(
                title, real_last_stmt_balance - computed_stmt_balance))
        lines.append(self.add_title_line(options, _(
            "Equal Last Statement Balance"), real_last_stmt_balance))
        return lines
