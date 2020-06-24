# coding: utf-8

import logging

from odoo import api, fields, models, tools, _
from datetime import datetime

_logger = logging.getLogger(__name__)

class Product(models.Model):
    _inherit='product.product'

    @api.multi
    def write(self, vals):

        is_website_publish = vals.get("is_website_publish")
        __last_update = vals.get("__last_update")

        if is_website_publish:
            self.product_tmpl_id.update({"bck_stock_date": None})

        else:
            self.product_tmpl_id.update({"bck_stock_date": datetime.now()})

        result = super(Product, self).write(vals)

        return result