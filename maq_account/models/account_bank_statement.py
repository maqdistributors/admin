# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.osv import expression
from odoo.tools import float_compare, float_round, float_repr
from datetime import datetime, timedelta


class AccountBankStatement(models.Model):
    _inherit = 'account.bank.statement'

    @api.multi
    def reconciliation_widget_preprocess(self):
        """ Get statement lines of the specified statements or all unreconciled statement lines and try to automatically reconcile them / find them a partner.
            Return ids of statement lines left to reconcile and other data for the reconciliation widget.
        """
        statements = self
        # NB : The field account_id can be used at the statement line creation/import to avoid the reconciliation process on it later on,
        # this is why we filter out statements lines where account_id is set

        sql_query = """SELECT stl.id
                        FROM account_bank_statement_line stl
                        WHERE account_id IS NULL AND stl.amount != 0.0 AND not exists (select 1 from account_move_line aml where aml.statement_line_id = stl.id)
                            AND company_id = %s
                """
        params = (self.env.user.company_id.id,)
        if statements:
            sql_query += ' AND stl.statement_id IN %s'
            params += (tuple(statements.ids),)
        '''Override the line number 30 to bring account bank statement lines in ascending order while doing reconciliation process.
           Previously it was sql_query += ' ORDER BY stl.id' '''
        sql_query += ' ORDER BY stl.date,stl.id'
        self.env.cr.execute(sql_query, params)
        st_lines_left = self.env['account.bank.statement.line'].browse(
            [line.get('id') for line in self.env.cr.dictfetchall()])
        # try to assign partner to bank_statement_line
        stl_to_assign = st_lines_left.filtered(lambda stl: not stl.partner_id)
        refs = set(stl_to_assign.mapped('name'))
        if stl_to_assign and refs\
           and st_lines_left[0].journal_id.default_credit_account_id\
           and st_lines_left[0].journal_id.default_debit_account_id:

            sql_query = """SELECT aml.partner_id, aml.ref, stl.id
                            FROM account_move_line aml
                                JOIN account_account acc ON acc.id = aml.account_id
                                JOIN account_bank_statement_line stl ON aml.ref = stl.name
                            WHERE (aml.company_id = %s 
                                AND aml.partner_id IS NOT NULL) 
                                AND (
                                    (aml.statement_id IS NULL AND aml.account_id IN %s) 
                                    OR 
                                    (acc.internal_type IN ('payable', 'receivable') AND aml.reconciled = false)
                                    )
                                AND aml.ref IN %s
                                """
            params = (self.env.user.company_id.id, (st_lines_left[0].journal_id.default_credit_account_id.id, st_lines_left[
                      0].journal_id.default_debit_account_id.id), tuple(refs))
            if statements:
                sql_query += 'AND stl.id IN %s'
                params += (tuple(stl_to_assign.ids),)
            self.env.cr.execute(sql_query, params)
            results = self.env.cr.dictfetchall()
            st_line = self.env['account.bank.statement.line']
            for line in results:
                st_line.browse(line.get('id')).write(
                    {'partner_id': line.get('partner_id')})
        return {
            'st_lines_ids': st_lines_left.ids,
            'notifications': [],
            'statement_name': len(statements) == 1 and statements[0].name or False,
            'journal_id': statements and statements[0].journal_id.id or False,
            'num_already_reconciled_lines': 0,
        }
