# -*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models, _
from odoo.exceptions import UserError


class ReportSaleOrderLabel(models.AbstractModel):
    _name = 'report.maqabim_purchase.report_solabel'

    @api.model
    def _get_report_values(self, docids, data=None):
        if not data.get('form'):
            raise UserError(_("Form content is missing, this report cannot be printed."))

        order_ids = self.env.context.get('active_ids', [])
        orders = self.env['sale.order'].browse(order_ids)
        report_format = data['form'].get('formats')
        return {
            'doc_ids': order_ids,
            'doc_model': 'sale.order',
            'docs': orders,
            'data': data,
            'report_format': report_format
        }
