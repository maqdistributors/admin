# -*- coding: utf-8 -*-

import time
from odoo import models, fields, api, _


class ShopifyProductUpdate(models.TransientModel):
    _name = 'update.shopify.product'
    _description = "Shopify Product Update"

    @api.multi
    def update_shopify_product_template(self):
        shopify_prod_obj = self.env['shopify.product.template']
        for rec in self:
            active_ids = rec._context.get('active_ids')
            shopify_prod_search = shopify_prod_obj.search(
                [('id', 'in', active_ids), ("shopify_prod_tmpl_id", "!=", False)])
            # Add counter b'coz we can send only 2 request per second
            count = 1
            for product in shopify_prod_search:
                product.update_shopify_product()
                if (count % 2 == 0):
                    time.sleep(0.5)
                count += 1
