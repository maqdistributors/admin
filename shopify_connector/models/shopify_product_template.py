# -*- coding: utf-8 -*-

import shopify
import logging

from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

from odoo import models, fields, api, _
from odoo.tools.translate import html_translate
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)
_product_list = []

class ShopifyProductTemplate(models.Model):
    _name = 'shopify.product.template'
    _description = 'Shopify Product Template'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _rec_name = 'product_tmpl_id'

    @api.multi
    @api.onchange('shopify_config_id')
    def onchange_shopify_config(self):
        '''
        Set Vendor and product type according to shopify config ID
        '''
        for rec in self:
            if rec.shopify_config_id:
                rec.vendor = ""
                rec.product_type = ""
                return {'domain': {'vendor': [('shopify_config_id', '=', rec.shopify_config_id.id)],
                                   'product_type': [('shopify_config_id', '=', rec.shopify_config_id.id)]}}

    name = fields.Char("Name", help="Enter Name", track_visibility='onchange')
    shopify_config_id = fields.Many2one("shopify.config", "Shopify Config",
                                        help="Enter Shopify Config", track_visibility='onchange', required=True)
    body_html = fields.Html("Body Html", help="Enter Body Html",
                            track_visibility='onchange', translate=html_translate)
    vendor = fields.Many2one("shopify.vendor", "Shopify Vendor",
                             help="Enter Shopify Vendor", track_visibility='onchange')
    product_type = fields.Many2one("shopify.product.type", "Shopify Product Type",
                                   help="Enter Shopify Product Type", track_visibility='onchange')
    shopify_published = fields.Boolean(
        "Shopify Published",  help="Enter Shopify Published", track_visibility='onchange', default=True)
    shopify_prod_tmpl_id = fields.Char(
        "Shopify Product Template ID", help="Enter Shopify Product Template ID", track_visibility='onchange', readonly=True)
    meta_fields_ids = fields.Many2many("shopify.metafields",
                                     help="Enter Shopify Metafields", track_visibility='onchange')
    image_ids = fields.Many2many("shopify.images", 'shopify_product_template_images_rel', 'product_template_id',
                                 'image_id', "Shopify Images", help="Enter Shopify Metafields", track_visibility='onchange')
    product_tmpl_id = fields.Many2one(
        "product.template", "Product Template", help="Enter Product Template", required=True, track_visibility='onchange')
    shopify_error_log = fields.Text(
        "Shopify Error", help="Error occurs while exporting move to the shopify",
        readonly=True)
    # check_multi_click = fields.Boolean("Multi Click", help="Check Multi Click?", track_visibility='onchange', readonly=True)

    r_prod_tags = fields.Many2many(related='product_tmpl_id.prod_tags_ids', string='Product Tags', track_visibility='onchange')
    r_prov_tags = fields.Many2many(related='product_tmpl_id.province_tags_ids', string='Province Tags', track_visibility='onchange')
    r_allowed_variants = fields.One2many(related='product_tmpl_id.allowed_variants_ids', string='Allowed Variants', track_visibility='onchange', readonly=True)
    last_updated_date = fields.Datetime(string='Last Updated Date', readonly=True)

    @api.model
    def create(self, vals):
        '''
        Prevent the user to create a shopify product template record with the same shopify config.
        '''
        res = super(ShopifyProductTemplate, self).create(vals)
        product_template_id = vals.get('product_tmpl_id')
        shopify_config_id = vals.get('shopify_config_id')
        shopify_product_templates = self.env['shopify.product.template'].search_count(
            [('product_tmpl_id', '=', product_template_id), ('shopify_config_id', '=', shopify_config_id)])
        if shopify_product_templates > 1:
            raise ValidationError(
                _("You cannot create multiple records for same shopify configuration"))
        return res

    @api.multi
    def write(self, vals):
        '''
        Prevent the user to update a shopify product template record with the same shopify config.
        '''
        res = super(ShopifyProductTemplate, self).write(vals)
        for rec in self:
            product_template_id = rec.product_tmpl_id.id
            shopify_config_id = vals.get('shopify_config_id')
            shopify_product_variants_count = self.env['shopify.product.template'].search_count(
                [('product_tmpl_id', '=', product_template_id), ('shopify_config_id', '=', shopify_config_id)])
            shopify_product_variants = self.env['shopify.product.template'].search(
                [('product_tmpl_id', '=', product_template_id), ('shopify_config_id', '=', shopify_config_id)])
            if shopify_product_variants_count > 1:
                raise ValidationError(
                    _("You cannot create multiple records for same shopify configuration"))
        return res

    @api.multi
    def export_shopify(self):
        '''
        This method is called by export button and it checks if product or province tags are set and then,
        it calls the export product method on shopify config object.
        '''
        for rec in self:
            if not rec.shopify_prod_tmpl_id:
                shopify_config_rec = rec.shopify_config_id
                if rec.product_tmpl_id.prod_tags_ids or rec.product_tmpl_id.province_tags_ids:
                    shopify_config_rec.export_product(rec)
                elif not (rec.product_tmpl_id.prod_tags_ids or rec.product_tmpl_id.province_tags_ids):
                    raise ValidationError(
                        _("Please select atleast 1 product or province tags before exporting product to shopify!"))

    @api.multi
    def update_shopify_product(self):
        '''
        Process shopify product template updation from odoo to shopify

        1. Check the connection of odoo with shopify.
        2. Get the respective field values like shopify product template id, product and province tags,
           product template name, body html, vendor, product type.
        3. If the product exists on shopify then only it will update, else it will throw validation error
        4. Set all the fields values on shopify product and save the shopify product object.
        '''
        self.shopify_config_id.test_connection()
        for rec in self:
            record_id = rec.id
            product_tmpl_rec = rec.product_tmpl_id

            if record_id in _product_list:
                return True
            _product_list.append(record_id)

            if not (product_tmpl_rec.prod_tags_ids or product_tmpl_rec.province_tags_ids):
                if record_id in _product_list:
                    _product_list.remove(record_id)
                raise ValidationError(_("Please select atleast 1 product or province tags before exporting product to shopify!"))

            if product_tmpl_rec.sale_ok and product_tmpl_rec.purchase_ok:
                try:
                    shopify_product_id = str(rec.shopify_prod_tmpl_id)
                    is_shopify_product = shopify.Product.exists(shopify_product_id)
                    if is_shopify_product:
                        prod_tags = product_tmpl_rec.prod_tags_ids
                        province_tags = product_tmpl_rec.province_tags_ids
                        str_prod_province_tags = []
                        for prod_tag in prod_tags:
                            str_prod_province_tags.append(prod_tag.name)
                        for prov_tag in province_tags:
                            str_prod_province_tags.append(prov_tag.name)
                        product_template_tags = ",".join(str_prod_province_tags)
                        product_template_image = product_tmpl_rec.image.decode('utf-8') if product_tmpl_rec.image else False
                        product_template_metafields = rec.meta_fields_ids
                        product_template_metafields_keys = [mt.key for mt in product_template_metafields]
                        shopify_product = shopify.Product({'id': shopify_product_id, 'published': rec.shopify_published})
                        shopify_product_metafields = shopify_product.metafields()
                        shopify_product_metafields_keys = [mt.key for mt in shopify_product_metafields]
                        image_list = []
                        if product_template_image:
                            image_list = [{'attachment': product_template_image,
                                           'position': 1}]
                        for product_image in product_tmpl_rec.product_image_ids:
                            image_list.append({'attachment': product_image.image.decode('utf-8')})
                        get_images = shopify.Image.find(product_id=rec.shopify_prod_tmpl_id)
                        if get_images:
                            for images in get_images:
                                images.destroy()
                        if image_list:
                            shopify_product.images = image_list
                            shopify_product.save()

                        # Get attribute data from product template recordset
                        options = []
                        for attribute_line in product_tmpl_rec.attribute_line_ids:
                            options_val = {}
                            options_val.update(
                                {'name': attribute_line.attribute_id.name})
                            values = []
                            for value_id in attribute_line.value_ids:
                                values.append(value_id.name)
                            options_val.update({'values': values})
                            options += [options_val]

                        if product_template_metafields_keys == shopify_product_metafields_keys and (len(product_template_metafields_keys) and len(shopify_product_metafields_keys)) > 0:
                            for temp_metafield in product_template_metafields:
                                for metafield in shopify_product_metafields:
                                    if temp_metafield.key == metafield.key:
                                        metafield.attributes.update(
                                            {'value': temp_metafield.value,
                                             'value_type': temp_metafield.value_type})
                                    metafield.save()
                        else:
                            if shopify_product_metafields and len(shopify_product_metafields) > 0:
                                for mt in shopify_product_metafields:
                                    mt.destroy()
                            if product_template_metafields and len(product_template_metafields) > 0:
                                for meta_rec in product_template_metafields:
                                    shopify_product.add_metafield(shopify.Metafield({'namespace': meta_rec.namespace or '',
                                                        'key': meta_rec.key or '',
                                                        'value': meta_rec.value or '',
                                                        'value_type': meta_rec.value_type or ''}))
                        shopify_product.title = product_tmpl_rec.name
                        shopify_product.body_html = rec.body_html if rec.body_html else ''
                        shopify_product.vendor = rec.vendor.name
                        shopify_product.product_type = rec.product_type.name
                        shopify_product.tags = product_template_tags
                        if options:
                            shopify_product.options = options
                        success = shopify_product.save()
                        # The code is written to update the shopify variants along with templates
                        shopify_product_products_list = []
                        product_variants = product_tmpl_rec.product_variant_ids.ids
                        shopify_product_search = self.env['shopify.product.product'].search([('product_variant_id','in',product_variants),
                                                                        ('shopify_config_id','=',rec.shopify_config_id.id)])
                        for shopify_prod in shopify_product_search:
                            if shopify_prod.shopify_product_id:
                                shopify_prod.update_shopify_variant()
                            else:
                                shopify_prod.export_shopify_variant()
                        rec.update({'last_updated_date':datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT)})
                        if record_id in _product_list:
                            _product_list.remove(record_id)
                    else:
                        if record_id in _product_list:
                            _product_list.remove(record_id)
                        raise ValidationError(_("Product Template does not exist in shopify !"))
                except Exception as e:
                    _logger.error('Error occurs while updating product template on shopify: %s', e)
                    if record_id in _product_list:
                        _product_list.remove(record_id)
                    pass
            else:
                if record_id in _product_list:
                    _product_list.remove(record_id)
                raise ValidationError(_("A Product should be 'Can be Sold' and 'Can be Purchased' before updation"))
