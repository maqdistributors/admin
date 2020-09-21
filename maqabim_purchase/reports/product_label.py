# -*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models, _
from odoo.exceptions import UserError


class ReportProductLabel(models.AbstractModel):
    _name = 'report.maqabim_purchase.report_productlabel'

    @api.model
    def get_report_values(self, docids, data=None):
        if not data.get('form'):
            raise UserError(_("Form content is missing, this report cannot be printed."))

        product_ids = self.env.context.get('active_ids', [])
        products = self.env['product.product'].browse(product_ids)
        report_format = data['form'].get('formats')
        pqty_by_product = data['form'].get('pqty_by_product')
        return {
            'doc_ids': product_ids,
            'doc_model': 'product.product',
            'docs': products,
            'data': data,
            'report_format': report_format,
            'pqty_by_product': pqty_by_product,
        }
