# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ProductProduct(models.Model):
    _inherit = "product.product"

    shopify_product_product_ids = fields.One2many(
        "shopify.product.product", "product_variant_id", "Shopify Product Variants", help="Enter Shopify Product Variants")
    shopify_shipping_product = fields.Boolean(
        "Is Shopify Shipping Product", help="Check if this is product use a shipping product while import order?", track_visibility='onchange')
    shopify_discount_product = fields.Boolean(
        "Is Shopify Discount Product", help="Check if this is product use a discount product while import order?", track_visibility='onchange')
    # shopify_weight = fields.Float(
    #     "Weight", help="Enter Shopify Product Variants", track_visibility="onchange")
    # shopify_uom = fields.Many2one(
    #     "product.uom", "Shopify UOM", help="Enter Shopify UOM", domain=[('is_shopify_uom','=',True)], track_visibility="onchange")

    @api.multi
    def _check_default_code_uniq_product(self):
        '''
        Prevent the default code duplication when creating product variant
        '''
        for rec in self:
            if rec.default_code:
                search_product_count = self.search_count(
                    [('default_code', '=', rec.default_code)])
                if search_product_count > 1:
                    return False
        return True

    _constraints = [
        (_check_default_code_uniq_product,
         'Default Code must be unique per Product!', ['default_code']),
    ]

    @api.model
    def create(self, vals):
        """
        Restrict a user from creating multiple shipping products and multiple discount products for Shopify.
        """
        res = super(ProductProduct, self).create(vals)
        shopify_shipping_product = vals.get('shopify_shipping_product') or self.shopify_shipping_product
        shopify_discount_product = vals.get('shopify_discount_product') or self.shopify_discount_product
        if shopify_shipping_product:
            shipping_product_variant_count = self.search_count([('type','=','service'),('shopify_shipping_product', '=', True)])
            if shipping_product_variant_count > 1:
                raise ValidationError(_("Shipping Product Already Exists in the system !"))
        if shopify_discount_product:
            discount_product_variant_count = self.search_count([('type','=','service'),('shopify_discount_product', '=', True)])
            if discount_product_variant_count > 1:
                raise ValidationError(_("Discount Product Already Exists in the system !"))
        return res

    @api.multi
    def write(self, vals):
        """
        Restrict a user from creating multiple shipping products and multiple discount products for Shopify.
        """
        res = super(ProductProduct, self).write(vals)
        shopify_shipping_product = vals.get('shopify_shipping_product') or self.shopify_shipping_product
        shopify_discount_product = vals.get('shopify_discount_product') or self.shopify_discount_product
        if shopify_shipping_product:
            shipping_product_variant_count = self.search_count([('type','=','service'),('shopify_shipping_product', '=', True)])
            if shipping_product_variant_count > 1:
                raise ValidationError(_("Shipping Product Already Exists in the system !"))
        if shopify_discount_product:
            discount_product_variant_count = self.search_count([('type','=','service'),('shopify_discount_product', '=', True)])
            if discount_product_variant_count > 1:
                raise ValidationError(_("Discount Product Already Exists in the system !"))
        return res
