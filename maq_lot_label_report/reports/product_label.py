# -*- coding:utf-8 -*-

from odoo import api, models, _
from odoo.exceptions import UserError


class ReportProductLabel(models.AbstractModel):
    _name = 'report.maq_lot_label_report.report_productlabel'

    @api.model
    def _get_report_values(self, docids, data=None):
        if not data.get('form'):
            raise UserError(
                _("Form content is missing, this report cannot be printed."))

        product_ids = self.env.context.get('active_ids', [])
        products = self.env['product.product'].browse(product_ids)
        report_format = data['form'].get('label_formats')
        pqty_by_product = data['form'].get('pqty_by_product')
        lot_by_product = data['form'].get('lot_by_product')
        lot_by_product_dict = {}
        for item in lot_by_product:
            item_value = list(lot_by_product[item])
            lot_by_product_dict.update(
                {item: self.env['stock.production.lot'].browse(item_value)})
        return {
            'doc_ids': product_ids,
            'doc_model': 'product.product',
            'docs': products,
            'data': data,
            'report_format': report_format,
            'pqty_by_product': pqty_by_product,
            'lot_by_product_dict': lot_by_product_dict,
        }
