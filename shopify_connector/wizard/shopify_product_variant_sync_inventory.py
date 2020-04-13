# -*- coding: utf-8 -*-

import shopify
import time
from odoo import models, fields, api, _


class ShopifyVariantInventorySync(models.TransientModel):
    _name = 'shopify.variant.inventory.sync'
    _description = "Shopify Product variant Sync"

    @api.multi
    def shopify_product_variant_inventory_sync(self):
        shopify_prod_obj = self.env['shopify.product.product']
        stock_quant_obj = self.env['stock.quant']
        for rec in self:
            active_ids = rec._context.get('active_ids')
            shopify_prod_search = shopify_prod_obj.search(
                [('id', 'in', active_ids), ("shopify_product_id", "not in", ['', False])])
            # Add counter b'coz we can send only 2 request per second
            count = 1
            for prod in shopify_prod_search:
                shopify_variant_id = prod
                inventory_item_id = prod.shopify_inventory_item_id
                shopify_config_id = prod.shopify_config_id.id
                prod.shopify_config_id.test_connection()
                shopify_locations_records = self.env['shopify.locations'].sudo().search(
                    [('shopify_config_id', '=', shopify_config_id)])
                for shopify_locations_record in shopify_locations_records:
                    shopify_location = shopify_locations_record.shopify_location_id
                    shopify_location_id = shopify_locations_record.id
                    available_qty = 0
                    quant_locations = stock_quant_obj.sudo().search([('location_id.usage', '=', 'internal'), (
                        'product_id', '=', shopify_variant_id.product_variant_id.id), ('location_id.shopify_location_ids', 'in', [shopify_location_id])])
                    if quant_locations:
                        for quant_location in quant_locations:
                            available_qty += quant_location.quantity
                    location = shopify.InventoryLevel.set(
                        shopify_location, inventory_item_id, int(available_qty))
                if (count % 2 == 0):
                    time.sleep(0.5)
                count += 1
