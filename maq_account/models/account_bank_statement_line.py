# -*- coding: utf-8 -*-

from odoo import api, models


class AccountReconciliation(models.AbstractModel):
    _inherit = 'account.reconciliation.widget'

    @api.model
    def get_move_lines_for_bank_statement_line(self, st_line_id, partner_id=None, excluded_ids=None, search_str=False, offset=0, limit=None):
        """ Returns move lines for the bank statement reconciliation widget,
            formatted as a list of dicts

            :param st_line_id: ids of the statement lines
            :param partner_id: optional partner id to select only the moves
                line corresponding to the partner
            :param excluded_ids: optional move lines ids excluded from the
                result
            :param search_str: optional search (can be the amout, display_name,
                partner name, move line name)
            :param offset: offset of the search result (to display pager)
            :param limit: number of the result to search
        """
        st_line = self.env['account.bank.statement.line'].browse(st_line_id)

        # Blue lines = payment on bank account not assigned to a statement yet
        aml_accounts = [
            st_line.journal_id.default_credit_account_id.id,
            st_line.journal_id.default_debit_account_id.id
        ]

        if partner_id is None:
            partner_id = st_line.partner_id.id

        domain = self._domain_move_lines_for_reconciliation(st_line, aml_accounts, partner_id, excluded_ids=excluded_ids, search_str=search_str)
        recs_count = self.env['account.move.line'].search_count(domain)
        aml_recs = self.env['account.move.line'].search(domain, offset=offset, limit=limit, order="date_maturity asc, id asc")
        target_currency = st_line.currency_id or st_line.journal_id.currency_id or st_line.journal_id.company_id.currency_id
        return self._prepare_move_lines(aml_recs, target_currency=target_currency, target_date=st_line.date, recs_count=recs_count)


    @api.model
    def _get_move_line_reconciliation_proposition(self, account_id, partner_id=None):
        """ Returns two lines whose amount are opposite """

        Account_move_line = self.env['account.move.line']

        ir_rules_query = Account_move_line._where_calc([])
        Account_move_line._apply_ir_rules(ir_rules_query, 'read')
        from_clause, where_clause, where_clause_params = ir_rules_query.get_sql()
        where_str = where_clause and (" WHERE %s" % where_clause) or ''

        # Get pairs
        query = """
            SELECT a.id, b.id
            FROM account_move_line a, account_move_line b
            WHERE a.id != b.id
            AND a.amount_residual = -b.amount_residual
            AND NOT a.reconciled
            AND a.account_id = %s
            AND (%s IS NULL AND b.account_id = %s)
            AND (%s IS NULL AND NOT b.reconciled OR b.id = %s)
            AND (%s is NULL OR (a.partner_id = %s AND b.partner_id = %s))
            AND a.id IN (SELECT id FROM {0})
            AND b.id IN (SELECT id FROM {0})
            ORDER BY a.date asc
            LIMIT 1
            """.format(from_clause + where_str)
        move_line_id = self.env.context.get('move_line_id') or None
        params = [
            account_id,
            move_line_id, account_id,
            move_line_id, move_line_id,
            partner_id, partner_id, partner_id,
        ] + where_clause_params + where_clause_params
        self.env.cr.execute(query, params)

        pairs = self.env.cr.fetchall()

        if pairs:
            return Account_move_line.browse(pairs[0])
        return Account_move_line
