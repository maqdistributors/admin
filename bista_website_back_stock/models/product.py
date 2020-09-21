# coding: utf-8

import logging

from odoo import api, fields, models, tools, _
from datetime import datetime

_logger = logging.getLogger(__name__)


class Product(models.Model):
    _inherit = 'product.product'

    @api.multi
    def write(self, vals):
        __last_update = vals.get("__last_update")
        sale_ok = vals.get('sale_ok')
        if sale_ok:
            vals['is_website_publish'] = False
        elif sale_ok is None:
            sale_ok = self.product_tmpl_id.sale_ok
        is_website_publish = vals.get("is_website_publish")
        if is_website_publish == True and sale_ok == True:
            self.product_tmpl_id.update({"bck_stock_date": None})
        elif is_website_publish == False and sale_ok == True:
            self.product_tmpl_id.update({"bck_stock_date": datetime.now()})
        else:
            self.product_tmpl_id.update({"bck_stock_date": None})
            vals['is_website_publish'] = False
        result = super(Product, self).write(vals)
        return result
