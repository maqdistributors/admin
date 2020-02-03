# -*- coding: utf-8 -*-

from odoo import models, api
from datetime import timedelta
from odoo.tools import float_is_zero


class AccountReconcileModel(models.Model):

    _inherit = 'account.reconcile.model'

    @api.multi
    def _check_range_moves(self, available_candidates, line_residual, line_date):
        less_count = 1
        great_count = 1
        loop_count = 1
        less_range = 3
        great_range = 3
        less_range_date_list = [line_date - timedelta(r) for r in range(1, 4)]
        great_range_date_list = [line_date + timedelta(r) for r in range(1, 4)]
        lesser_date_available_candidates = list(filter(lambda lesser_candidate: lesser_candidate['aml_amount_residual'] == line_residual and lesser_candidate['aml_date_maturity'] < line_date and lesser_candidate['aml_date_maturity'] in less_range_date_list, available_candidates))
        greater_date_available_candidates = list(filter(lambda greater_candidate: greater_candidate['aml_amount_residual'] == line_residual and greater_candidate['aml_date_maturity'] > line_date and greater_candidate['aml_date_maturity'] in great_range_date_list, available_candidates))
        if lesser_date_available_candidates:
            lesser_date_available_candidates = sorted(lesser_date_available_candidates, key=lambda k: k['aml_date_maturity'], reverse=True)
        if greater_date_available_candidates:
            greater_date_available_candidates = sorted(greater_date_available_candidates, key=lambda k: k['aml_date_maturity'])
        lesser_dt_final_avail_can = []
        if lesser_date_available_candidates:
            for ava_can in lesser_date_available_candidates:
                lesser_dt_final_avail_can.append(ava_can['aml_date_maturity'])
        greater_dt_final_avail_can = []
        if greater_date_available_candidates:
            for ava_can in greater_date_available_candidates:
                greater_dt_final_avail_can.append(ava_can['aml_date_maturity'])
        total_dt_final_avail_can = lesser_dt_final_avail_can + greater_dt_final_avail_can
        if total_dt_final_avail_can:
            for dt_final in total_dt_final_avail_can:
                if lesser_dt_final_avail_can and (line_date - timedelta(less_count)) in lesser_dt_final_avail_can:
                    if len(lesser_dt_final_avail_can) > 1:
                        date_maturity_before_dt = line_date - \
                            timedelta(less_count)
                        available_candidates = [ava_can for ava_can in lesser_date_available_candidates if ava_can['aml_date_maturity'] == date_maturity_before_dt]
                        if len(available_candidates) > 1:
                            available_candidates = [available_candidates[0]]
                        break
                    if len(lesser_dt_final_avail_can) == 1 and not len(greater_dt_final_avail_can) > 1:
                        available_candidates = [ava_can for ava_can in lesser_date_available_candidates if ava_can['aml_date_maturity'] == lesser_dt_final_avail_can[0]]
                        break
                elif greater_dt_final_avail_can and (line_date + timedelta(great_count)) in greater_dt_final_avail_can:
                    if len(greater_dt_final_avail_can) > 1:
                        date_maturity_after_dt = line_date + \
                            timedelta(great_count)
                        available_candidates = [ava_can for ava_can in greater_date_available_candidates if ava_can['aml_date_maturity'] == date_maturity_after_dt]
                        if len(available_candidates) > 1:
                            available_candidates = [available_candidates[0]]
                        break
                    if len(greater_dt_final_avail_can) == 1 and not len(lesser_dt_final_avail_can) > 1:
                        available_candidates = [ava_can for ava_can in greater_date_available_candidates if ava_can['aml_date_maturity'] == greater_dt_final_avail_can[0]]
                        break
                elif len(lesser_dt_final_avail_can) <= 1 or len(greater_dt_final_avail_can) <= 1:
                    if len(lesser_dt_final_avail_can) == 1 and not len(greater_dt_final_avail_can) > 1:
                        available_candidates = [ava_can for ava_can in lesser_date_available_candidates if ava_can['aml_date_maturity'] == lesser_dt_final_avail_can[0]]
                        break
                    if len(greater_dt_final_avail_can) == 1 and not len(lesser_dt_final_avail_can) > 1:
                        available_candidates = [ava_can for ava_can in greater_date_available_candidates if ava_can['aml_date_maturity'] == greater_dt_final_avail_can[0]]
                        break
                less_count += 1
                great_count += 1
                loop_count += 1
                if loop_count == len(total_dt_final_avail_can):
                    less_count = great_count = loop_count = 1
                    break
            return available_candidates
        elif not total_dt_final_avail_can and len(available_candidates) >= 1:
            for candidate in available_candidates:
                if candidate['aml_amount_residual'] == line_residual and candidate['aml_date_maturity'] <= line_date:
                    available_candidates = [candidate]
                    break
                elif candidate['aml_amount_residual'] == line_residual and candidate['aml_date_maturity'] >= line_date:
                    available_candidates = [candidate]
                    break
            return available_candidates

    @api.multi
    def _apply_rules(self, st_lines, excluded_ids=None, partner_map=None):
        ''' Apply criteria to get candidates for all reconciliation models.
        :param st_lines:        Account.bank.statement.lines recordset.
        :param excluded_ids:    Account.move.lines to exclude.
        :param partner_map:     Dict mapping each line with new partner eventually.
        :return:                A dict mapping each statement line id with:
            * aml_ids:      A list of account.move.line ids.
            * model:        An account.reconcile.model record (optional).
            * status:       'reconciled' if the lines has been already reconciled, 'write_off' if the write-off must be
                            applied on the statement line.
        '''
        available_models = self.filtered(lambda m: m.rule_type != 'writeoff_button')

        results = dict((r.id, {'aml_ids': []}) for r in st_lines)

        if not available_models:
            return results

        ordered_models = available_models.sorted(key=lambda m: (m.sequence, m.id))

        grouped_candidates = {}

        # Type == 'invoice_matching'.
        # Map each (st_line.id, model_id) with matching amls.
        invoices_models = ordered_models.filtered(lambda m: m.rule_type == 'invoice_matching')
        if invoices_models:
            query, params = invoices_models._get_invoice_matching_query(st_lines, excluded_ids=excluded_ids, partner_map=partner_map)
            self._cr.execute(query, params)
            query_res = self._cr.dictfetchall()

            for res in query_res:
                grouped_candidates.setdefault(res['id'], {})
                grouped_candidates[res['id']].setdefault(res['model_id'], [])
                grouped_candidates[res['id']][res['model_id']].append(res)

        # Type == 'writeoff_suggestion'.
        # Map each (st_line.id, model_id) with a flag indicating the st_line matches the criteria.
        write_off_models = ordered_models.filtered(lambda m: m.rule_type == 'writeoff_suggestion')
        if write_off_models:
            query, params = write_off_models._get_writeoff_suggestion_query(st_lines, excluded_ids=excluded_ids, partner_map=partner_map)
            self._cr.execute(query, params)
            query_res = self._cr.dictfetchall()

            for res in query_res:
                grouped_candidates.setdefault(res['id'], {})
                grouped_candidates[res['id']].setdefault(res['model_id'], True)

        # Keep track of already processed amls.
        amls_ids_to_exclude = set()

        # Keep track of already reconciled amls.
        reconciled_amls_ids = set()

        # Iterate all and create results.
        for line in st_lines:
            line_currency = line.currency_id or line.journal_id.currency_id or line.company_id.currency_id
            line_residual = line.currency_id and line.amount_currency or line.amount
            line_date = line.date

            # Search for applicable rule.
            # /!\ BREAK are very important here to avoid applying multiple rules on the same line.
            for model in ordered_models:
                # No result found.
                if not grouped_candidates.get(line.id) or not grouped_candidates[line.id].get(model.id):
                    continue

                excluded_lines_found = False

                if model.rule_type == 'invoice_matching':
                    candidates = grouped_candidates[line.id][model.id]

                    # If some invoices match on the communication, suggest them.
                    # Otherwise, suggest all invoices having the same partner.
                    # N.B: The only way to match a line without a partner is through the communication.
                    first_batch_candidates = []
                    second_batch_candidates = []
                    for c in candidates:
                        # Don't take into account already reconciled lines.
                        if c['aml_id'] in reconciled_amls_ids:
                            continue

                        # Dispatch candidates between lines matching invoices with the communication or only the partner.
                        if c['communication_flag']:
                            first_batch_candidates.append(c)
                        elif not first_batch_candidates:
                            second_batch_candidates.append(c)
                    available_candidates = first_batch_candidates or second_batch_candidates

                    # Special case: the amount are the same, submit the line directly.
                    for c in available_candidates:
                        residual_amount = c['aml_currency_id'] and c['aml_amount_residual_currency'] or c['aml_amount_residual']

                        if float_is_zero(residual_amount - line_residual, precision_rounding=line_currency.rounding) and line.date == c['aml_date_maturity'] and c['aml_id'] not in amls_ids_to_exclude:
                            available_candidates = [c]
                            break
                    if len(available_candidates) > 1:
                        available_candidates = list(filter(lambda candidate: candidate['aml_amount_residual'] == line_residual and candidate['aml_date_maturity'] != line.date and candidate['aml_id'] not in amls_ids_to_exclude, available_candidates))
                        available_candidates = self._check_range_moves(available_candidates, line_residual, line_date)
                    # Needed to handle check on total residual amounts.
                    if first_batch_candidates or model._check_rule_propositions(line, available_candidates):
                        results[line.id]['model'] = model
                        # Add candidates to the result.
                        if available_candidates:
                            for candidate in available_candidates:
                                # Special case: the propositions match the rule but some of them are already consumed by
                                # another one. Then, suggest the remaining propositions to the user but don't make any
                                # automatic reconciliation.
                                if candidate['aml_id'] in amls_ids_to_exclude:
                                    excluded_lines_found = True
                                    continue
    
                                results[line.id]['aml_ids'].append(candidate['aml_id'])
                                amls_ids_to_exclude.add(candidate['aml_id'])

                        if excluded_lines_found:
                            break
                        # Create write-off lines.
                        move_lines = self.env['account.move.line'].browse(results[line.id]['aml_ids'])
                        partner = partner_map and partner_map.get(line.id) and self.env['res.partner'].browse(partner_map[line.id])
                        reconciliation_results = model._prepare_reconciliation(line, move_lines, partner=partner)

                        # A write-off must be applied.
                        if reconciliation_results['new_aml_dicts']:
                            results[line.id]['status'] = 'write_off'

                        # Process auto-reconciliation.
                        if model.auto_reconcile:
                            # An open balance is needed but no partner has been found.
                            if reconciliation_results['open_balance_dict'] is False:
                                break

                            new_aml_dicts = reconciliation_results['new_aml_dicts']
                            if reconciliation_results['open_balance_dict']:
                                new_aml_dicts.append(reconciliation_results['open_balance_dict'])
                            if not line.partner_id and partner:
                                line.partner_id = partner
                            counterpart_moves = line.process_reconciliation(
                                counterpart_aml_dicts=reconciliation_results['counterpart_aml_dicts'],
                                payment_aml_rec=reconciliation_results['payment_aml_rec'],
                                new_aml_dicts=new_aml_dicts,
                            )
                            results[line.id]['status'] = 'reconciled'
                            results[line.id]['reconciled_lines'] = counterpart_moves.mapped('line_ids')

                            # The reconciled move lines are no longer candidates for another rule.
                            reconciled_amls_ids.update(move_lines.ids)

                        # Break models loop.
                        break

                elif model.rule_type == 'writeoff_suggestion' and grouped_candidates[line.id][model.id]:
                    results[line.id]['model'] = model
                    results[line.id]['status'] = 'write_off'

                    # Create write-off lines.
                    partner = partner_map and partner_map.get(line.id) and self.env['res.partner'].browse(partner_map[line.id])
                    reconciliation_results = model._prepare_reconciliation(line, partner=partner)

                    # An open balance is needed but no partner has been found.
                    if reconciliation_results['open_balance_dict'] is False:
                        break

                    # Process auto-reconciliation.
                    if model.auto_reconcile:
                        new_aml_dicts = reconciliation_results['new_aml_dicts']
                        if reconciliation_results['open_balance_dict']:
                            new_aml_dicts.append(reconciliation_results['open_balance_dict'])
                        if not line.partner_id and partner:
                            line.partner_id = partner
                        counterpart_moves = line.process_reconciliation(
                            counterpart_aml_dicts=reconciliation_results['counterpart_aml_dicts'],
                            payment_aml_rec=reconciliation_results['payment_aml_rec'],
                            new_aml_dicts=new_aml_dicts,
                        )
                        results[line.id]['status'] = 'reconciled'
                        results[line.id]['reconciled_lines'] = counterpart_moves.mapped('line_ids')

                    # Break models loop.
                    break
        return results





