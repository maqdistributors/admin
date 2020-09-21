# -*- coding: utf-8 -*-

import random
from odoo import models, fields, api, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

#     def _cart_accessories(self):
#         for order in self:
#             current_website_id = self.env['website'].get_current_website()
#             website_company_id = current_website_id.company_id
#             accessory_products = []
#             for products in order.website_order_line.mapped('product_id'):
#                 for product in products:
#                     accessory_products += product.accessory_product_ids.ids
#         accessory_products = self.env['product.product'].browse(accessory_products).filtered(lambda product : product.company_id == website_company_id and product.website_published)
#         accessory_products -= order.website_order_line.mapped('product_id')
#         return random.sample(accessory_products, len(accessory_products))

    def _cart_accessories(self):
        """ Suggest accessories based on 'Accessory Products' of products in cart """
        for order in self:
            current_website_id = self.env['website'].get_current_website()
            website_company_id = current_website_id.company_id
            products = order.website_order_line.mapped('product_id')
            accessory_products = self.env['product.product']
            for line in order.website_order_line.filtered(lambda l: l.product_id):
                combination = line.product_id.product_template_attribute_value_ids + line.product_no_variant_attribute_value_ids
                accessory_products |= line.product_id.accessory_product_ids.filtered(lambda product:
                    product.website_published and
                    product not in products and
                    (product.company_id == website_company_id or not product.company_id) and
                    product._is_variant_possible(parent_combination=combination)
                )

            return random.sample(accessory_products, len(accessory_products))