# coding: utf-8

import logging

from odoo import api, fields, models, tools, _
from odoo.addons import decimal_precision as dp
# from odoo.exceptions import UserError, ValidationError
# from datetime import datetime

_logger = logging.getLogger(__name__)

class ProductTemplate(models.Model):
    _inherit='product.template'

    sales_pricelist = fields.Float(
        'Sales Pricelist', compute='_compute_sales_pricelist', default=1.0,
        digits=dp.get_precision('Product Price'),
        help="Base price to compute the customer price. Sometimes called the catalog price.")

    @api.multi
    def _compute_sales_pricelist(self):
        ppis = self.item_ids
        sales_pricelist = False
        for ppi in ppis:
            if ppi.min_quantity == 0 and ppi.date_start == False and ppi.date_end == False:
                sales_pricelist = ppi.fixed_price

        self.sales_pricelist = sales_pricelist
