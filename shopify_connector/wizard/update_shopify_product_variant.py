# -*- coding: utf-8 -*-

import time
from odoo import models, fields, api, _


class UpdateProductVariant(models.TransientModel):
    _name = 'update.shopify.variant'
    _description = "Shopify Product Variant Update"

    @api.multi
    def update_shopify_product_variant(self):
        shopify_product_variant_obj = self.env['shopify.product.product']
        for rec in self:
            active_ids = rec._context.get('active_ids')
            shopify_product_variant_search = shopify_product_variant_obj.search(
                [('id', 'in', active_ids), ("shopify_product_id", "!=", False)])
            # Add counter b'coz we can send only 2 request per second
            count = 1
            for product in shopify_product_variant_search:
                product.update_shopify_variant()
                if (count % 2 == 0):
                    time.sleep(0.5)
                count += 1
