# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    shopify_product_template_ids = fields.One2many("shopify.product.template", 'product_tmpl_id',
                                                   "Shopify Product Templates", help="Select Shopify Product Templates", track_visibility='onchange')
    prod_tags_ids = fields.Many2many("shopify.prod.tags", 'shopify_prod_tags_template_rel', 'prod_tag_id', 'product_template_id',
                                     "Prod. Tags", help="Enter Prod. Tags", track_visibility='onchange', domain=[('is_province', '=', False)])
    province_tags_ids = fields.Many2many("shopify.prod.tags", 'shopify_province_tags_template_rel', 'province_tag_id', 'product_template_id',
                                         "Province Tags", help="Enter Province Tags", track_visibility='onchange', domain=[('is_province', '=', True)])
    allowed_variants_ids = fields.One2many("shopify.product.product", "product_template_id",
                                           "Allowed Variants", help="Enter Allowed Variants", track_visibility='onchange', domain=lambda self: [('product_template_id', 'in', self.ids)])
    published_on_shopify = fields.Boolean(
        "Published on Shopify", help="Published on Shopify", track_visibility='onchange')

    @api.multi
    def _check_default_code_uniq_template(self):
        '''
        Prevent the default code duplication when creating product template
        '''
        for rec in self:
            if rec.default_code:
                search_product_count = self.search_count(
                    [('default_code', '=', rec.default_code)])
                if search_product_count > 1:
                    return False
        return True

    _constraints = [
        (_check_default_code_uniq_template,
         'Default Code must be unique per Product!', ['default_code']),
    ]

    @api.multi
    def write(self, vals):
        """
        Restrict a user from making can_be_sold and can_be_purchased false if a
        product is exported on Shopify.If we import SO who's is can be sold
        and can be purchased then it'll create an issue for creating a sales
        order or purchase order.
        """
        res = super(ProductTemplate, self).write(vals)
        for rec in self:
            can_be_sold = vals.get('sale_ok') or rec.sale_ok
            can_be_purchased = vals.get('purchase_ok') or rec.purchase_ok
            shopify_published_list = []
            if not can_be_sold or not can_be_purchased:
                shopify_product_templates = rec.shopify_product_template_ids
                for s_prod_temp in shopify_product_templates:
                    shopify_published_list.append(
                        s_prod_temp.shopify_published)
                if True in shopify_published_list:
                    raise ValidationError(
                        _("The product should be unpublished on shopify end as well!!"))
        return res
