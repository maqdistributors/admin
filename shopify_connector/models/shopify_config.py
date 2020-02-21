# -*- coding: utf-8 -*-

import shopify
import logging
import json

from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT

from odoo import models, fields, api, _
from odoo.exceptions import Warning, ValidationError

_logger = logging.getLogger(__name__)
_shopify_allow_weights = ['kg', 'lb', 'oz', 'g']

class ShopifyConfig(models.Model):
    _name = 'shopify.config'
    _description = 'Shopify Configuration'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _rec_name = 'name'

    name = fields.Char('Name', help='Name of Connection',
                       track_visibility='onchange', required=True)
    shop_url = fields.Char(string='Shop URL', required=True, help='Enter Shop URL, URL format should be https://SHOP_NAME.myshopify.com/admin',
                           placeholder='https://SHOP_NAME.myshopify.com/admin', track_visibility='onchange')
    api_key = fields.Char("Api Key", help='Enter the API Key',
                          track_visibility='onchange', required=True)
    password = fields.Char("Password", help='Enter the Password',
                           track_visibility='onchange', required=True)
    default_company_id = fields.Many2one(
        "res.company", "Default Company", help='Set default company', track_visibility='onchange', required=True)
    company_ids = fields.Many2many("res.company", 'shopify_config_res_company_rel', 'shopify_config_id',
                                   'company_id', "Companies", help='Set Companies', track_visibility='onchange', required=True)
    state = fields.Selection([('draft', 'Draft'), ('success', 'Success'), ('fail', 'Fail')],
                             string='Status', help='Connection status of records',
                             default='draft', track_visibility='onchange')
    active = fields.Boolean(
        string='Active', track_visibility='onchange', default="True")

    @api.model
    def create(self, vals):
        '''
        Check on record creation time if the default company is set in companies and
        restrict user to select only two companies.
        '''
        res = super(ShopifyConfig, self).create(vals)
        company_ids = vals['company_ids'][0][2]
        default_company_id = vals['default_company_id']
        if default_company_id not in company_ids:
            raise ValidationError(
                _("The chosen default company is not in the companies !"))
        if len(company_ids) > 2:
            raise ValidationError(
                _("You cannot select more than two companies !"))
        return res

    @api.multi
    def write(self, vals):
        '''
        Check on record updation time if the default company is set in companies and
        restrict user to select only two companies.
        '''
        res = super(ShopifyConfig, self).write(vals)
        default_company_id = vals.get(
            'default_company_id') or self.default_company_id.id
        if default_company_id not in self.company_ids.ids:
            raise ValidationError(
                _("The chosen default company is not in the companies !"))
        if len(self.company_ids.ids) > 2:
            raise ValidationError(
                _("You cannot select more than two companies !"))
        return res

    @api.multi
    def reset_to_draft(self):
        '''This method will set the shopify config to draft state'''
        for rec in self:
            rec.state = 'draft'
        return True

    @api.multi
    def test_connection(self):
        """
        This function check that shopify store is exist or not using api_key, password and shop_url
        """
        for rec in self:
#             try:
            api_key = rec.api_key or ''
            password = rec.password or ''
            shop_url = rec.shop_url or ''
            if api_key and password and shop_url:
                shopify.ShopifyResource.set_user(api_key)
                shopify.ShopifyResource.set_password(password)
                shopify.ShopifyResource.set_site(shop_url)
                shop = shopify.Shop.current()
                if not shop:
                    raise Warning(
                    _('Kindly check api key, password or shop url'))
            else:
                raise Warning(
                    _('Kindly check api key, password or shop url'))
#             except Exception as e:
#                 rec.update({'state': 'fail'})
#                 self._cr.commit()
#                 _logger.error('Invalid API key or access token: %s', e)
#                 raise Warning(
#                     _('UnauthorizedAccess: Invalid API key or access token.'))
        return True

    @api.multi
    def check_connection(self):
        """
        This function check that shopify store is exist or not using api_key, password and shop_url
        """
        for rec in self:
            try:
                api_key = rec.api_key or ''
                password = rec.password or ''
                shop_url = rec.shop_url or ''
                if api_key and password and shop_url:
                    shopify.ShopifyResource.set_user(api_key)
                    shopify.ShopifyResource.set_password(password)
                    shopify.ShopifyResource.set_site(shop_url)
                    shop = shopify.Shop.current()
                    if shop:
                        rec.update({'state': 'success'})
                    else:
                        rec.update({'state': 'fail'})
                else:
                    raise Warning(
                        _('Kindly check api key, password or shop url'))
            except Exception as e:
                rec.update({'state': 'fail'})
                self._cr.commit()
                _logger.error('Invalid API key or access token: %s', e)
                raise Warning(
                    _('UnauthorizedAccess: Invalid API key or access token.'))
        return True

    @api.multi
    def export_products_to_shopify(self):
        """
        Fetch a product template ids which need to be updated on shopify
        and pass it to the export_product
        """
        self.ensure_one()
        user_id = self.env.user.id
        product_tmpl_ids = self.env['shopify.product.template'].sudo(user_id).search(
            [('shopify_config_id', '=', self.id), ('shopify_prod_tmpl_id', 'in', ['', False])])
        
        list_prod = []

        for prod_tmpl in product_tmpl_ids:
            if not (prod_tmpl.product_tmpl_id.prod_tags_ids or prod_tmpl.product_tmpl_id.province_tags_ids):
                list_prod.append(prod_tmpl.product_tmpl_id.name or '')

        if list_prod:
            raise ValidationError(_("Following products doesn't have any province tags or product tags - \n %s"%(list_prod)))


        for prod_tmpl in product_tmpl_ids:
            self.export_product(prod_tmpl)

#         product_tmpl_ids = [44038]
#         return self.export_product(product_tmpl_ids)

    @api.multi
    def export_new_shopify_variants(self):
        '''
        Export newly created variant of a product to shopify
        '''
        self.ensure_one()
        user_id = self.env.user.id
        new_product_variant_ids = self.env['shopify.product.product'].sudo(user_id).search(
            [('shopify_config_id', '=', self.id),
             ('shopify_product_id', 'in', ['', False]),
             ('shopify_inventory_item_id', 'in', ['', False]),
             ('shopify_product_template_id', 'in', ['', False])
             ])
        if new_product_variant_ids:
            for new_product in new_product_variant_ids:
                new_product.export_shopify_variant()
        else:
            raise ValidationError(_('No New shopify product variants available to export !'))

    @api.multi
    def export_product(self, s_product_tmpl_ids, shopify_locations_records=False):
        """
        Process Product template and pass it to the shopify

        1. Fetch Shopify Locations base on the configuration from shopify.locations master
        2. Get Product template recordset from shopify_proouct_template masters
        3. Get Shopify product variants recordset using shopify_proouct_template masters
        4. Get attribute data from product template recordset
        5. Prepare product's variant vals using shopify_product_product  recordset
            5.1 Variant's SKU, as well as weight and weight unit, are fetching from product variant
            5.2 sale price is fetched from shopify_product_product master
        6. Prepare vals for images using product template image and image_ids records
        7. Get tags data from using product template recordset (prod_tags_ids & province_tags_ids)
        8. Create Product Template on Shopify using the above details
        9. If a product is created successfully, then update shopify_template_id in shopify_product_template master and marked shopify_publsihed True in shopify_product_template master (to identify the product is created published on Shopify in future we can use this field to make product publish and unpublish on Shopify) else update an error message in the shopify_error_log field.
        10. Now update variants details in Odoo system as well as variant inventory and icon images on Shopify
            10.1 Get shopify variant vals using shopify create recordset
            10.2 Update an image on shopify for the variant
            10.3 Update shopify_product_id, shopify_inventory_item_id and shopify_product_template_id in shopify_product_product master
            10.4 Update an inventory for product for all locations
        """
        self.test_connection()

        product_tmpl_obj = self.env['product.template']
        shopify_prod_obj = self.env['shopify.product.product']
        stock_quant_obj = self.env['stock.quant']
        shopify_config_id = self.id

        # Fetch Shopify Locations base on the configuration from
        # shopify.locations master
        if not shopify_locations_records:
            shopify_locations_records = self.env['shopify.locations'].sudo().search(
                [('shopify_config_id', '=', shopify_config_id)])

        # Get Product template recordset from shopify_proouct_template masters
        for s_product_tmpl_id in s_product_tmpl_ids:
            try:
                product_tmpl_id = s_product_tmpl_id.product_tmpl_id
                if product_tmpl_id.sale_ok and product_tmpl_id.purchase_ok:
                # TO DO: Create a one2many relation shopify_product_template
                # with shopify_product_product
                # Get Shopify product variants recordset using
                # shopify_proouct_template masters
                    products = shopify_prod_obj.sudo().\
                        search([('shopify_config_id', '=', shopify_config_id),
                                ('shopify_product_id', 'in', ['', False]),
                                ('product_variant_id', 'in', product_tmpl_id.product_variant_ids.ids)])
                    if products.ids:

                    # Get attribute data from product template recordset
                        options = []
                        for attribute_line in product_tmpl_id.attribute_line_ids:
                            options_val = {}
                            options_val.update(
                                {'name': attribute_line.attribute_id.name})
                            values = []
                            for value_id in attribute_line.value_ids:
                                values.append(value_id.name)
                            options_val.update({'values': values})
                            options += [options_val]

                        # Prepare product's variant vals using shopify_product_product  recordset
                        # - Variant's SKU, as well as weight and weight unit, are fetching from product variant while the price is fetched from shopify_product_product master
                        variants = []
                        for s_product in products:
                            variant_val = {}
                            product = s_product.product_variant_id
                            if product.default_code:
                                default_code = product.default_code

                                count = 1
                                for value in product.attribute_value_ids:
                                    variant_val.update({'option' + str(count): value.name})
                                    count += 1

                                    # variant_meta_rec = s_product.meta_fields_id
                                    # variant_meta_data_dict = {"key": variant_meta_rec.key or '',
                                    #                         "value": variant_meta_rec.value or '',
                                    #                         "value_type": variant_meta_rec.value_type or '',
                                    #                         "namespace": variant_meta_rec.namespace or ''}
                                    # if variant_meta_data_dict:
                                    #     variant_val.update({'metafields': [variant_meta_data_dict]})

                                # lst_price = s_product.lst_price if s_product.lst_price > 0 else product.lst_price

                                weight_unit = product.uom_id
                                if weight_unit and weight_unit.name in _shopify_allow_weights:
                                    variant_val.update({'weight': product.weight,
                                                        'weight_unit': weight_unit.name})
                                else:
                                    _logger.error(
                                        _('UOM is not define for product variant id!: %s') % str(product.id))

                                variant_val.update(
                                    {'price': s_product.lst_price,
                                     'sku': default_code,
                                     "inventory_management": "shopify"})
                                variants += [variant_val]
                            else:
                                raise ValidationError(_("Please set internal reference for product variant before exporting to shopify"))
                    else:
                        raise ValidationError(_('Please set alteast one product variant for shopify product export'))
                else:
                    raise ValidationError(_("A product should be 'Can be Sold' and 'Can be Purchased' before exporting"))

                # Prepare vals for images using product template image
                # and image_ids records
                images = []
                if product_tmpl_id.image:
                    images += [{'attachment': product_tmpl_id.image.decode("utf-8"),
                                'position': 1}]
                for product_image in product_tmpl_id.product_image_ids:
                    if product_image.image:
                        images += [{'attachment': product_image.image.decode("utf-8")}]

                # Get tags data from using product template recordset
                # (prod_tags_ids & province_tags_ids)
                prod_tags = product_tmpl_id.prod_tags_ids
                province_tags = product_tmpl_id.province_tags_ids
                str_prod_province_tags = []
                for prod_tag in prod_tags:
                    str_prod_province_tags.append(prod_tag.name)
                for prov_tag in province_tags:
                    str_prod_province_tags.append(prov_tag.name)
                tags = ",".join(str_prod_province_tags)


                # Create Product Template on Shopify using the above details
                new_product = shopify.Product()
                new_product.title = product_tmpl_id.name
                new_product.published = s_product_tmpl_id.shopify_published
                if s_product_tmpl_id.product_type:
                    new_product.product_type = s_product_tmpl_id.product_type.name  # "Snowboard"
                if s_product_tmpl_id.vendor:
                    new_product.vendor = s_product_tmpl_id.vendor.name  # "Burton"
                if tags:
                    new_product.tags = tags  # "Barnes & Noble, John's Fav, \"Big Air\""
                if s_product_tmpl_id.body_html:
                    new_product.body_html = str(s_product_tmpl_id.body_html)
                else:
                    new_product.body_html = ''
                if options:
                    new_product.options = options
                if variants:
                    new_product.variants = variants
                if images:
                    new_product.images = images
                success = new_product.save()  # returns false if the record is invalid

                # If a product is created successfully, then update
                # shopify_template_id in shopify_product_template master and
                # marked shopify_publsihed True in shopify_product_template
                # master (to identify the product is created published on
                # Shopify in future we can use this field to make product
                # publish and unpublish on Shopify) else update an error
                # message in the shopify_error_log field.
                if success:
                    # Now update variants details in Odoo system as well as variant inventory and icon images on Shopify
                    # s_product_tmpl_id.update({'shopify_published': True})
                    if s_product_tmpl_id.meta_fields_ids:
                        template_meta_rec = s_product_tmpl_id.meta_fields_ids
                        if template_meta_rec:
                            for meta_rec in template_meta_rec:
                                new_product.add_metafield(shopify.Metafield({'namespace': meta_rec.namespace or '',
                                    'key': meta_rec.key or '',
                                    'value': meta_rec.value or '',
                                    'value_type': meta_rec.value_type or ''}))

                    shopify_product_tmpl_id = new_product.id
                    if shopify_product_tmpl_id:
                        s_product_tmpl_id.update(
                            {'shopify_prod_tmpl_id': shopify_product_tmpl_id,
                             'shopify_published': True,
                             'last_updated_date':datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT)})
                        # Get shopify variant vals using shopify create
                        # recordset
                        for variant in new_product.variants:
                            variant_id = variant.id
                            inventory_item_id = variant.inventory_item_id
                            default_code = variant.sku
                            shopify_product_product = shopify_prod_obj.sudo().\
                                search([('shopify_config_id', '=', shopify_config_id),
                                        ('shopify_product_id',
                                         'in', ['', False]),
                                        ('product_template_id',
                                         '=', product_tmpl_id.id),
                                        ('default_code', '=', default_code)], limit=1)
                            product_variant_rec = shopify_product_product.product_variant_id


                            # Update an image on shopify for the variant
                            if product_variant_rec:
                                variant_image = product_variant_rec.image
                                if variant_image:
                                    image = shopify.Image()
                                    image.product_id = shopify_product_tmpl_id
                                    image.attachment = variant_image.decode("utf-8")
#                                     image.variant_ids = [variant_id]
                                    image.save()
                                    variant.image_id = image.id
                                    variant.save()
                            if shopify_product_product:
                                # Update shopify_product_id,
                                # shopify_inventory_item_id and
                                # shopify_product_template_id in
                                # shopify_product_product master
                                shopify_product_product.sudo().update({'shopify_product_id': variant_id,
                                                                       'shopify_product_template_id': s_product_tmpl_id.id,
                                                                       'shopify_inventory_item_id': inventory_item_id,
                                    'last_updated_date':datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT)})

                                variant_meta_rec = shopify_product_product.meta_fields_ids
                                if variant_meta_rec:
                                    for meta_rec in variant_meta_rec:
                                        variant.add_metafield(shopify.Metafield({'namespace': meta_rec.namespace or '',
                                            'key': meta_rec.key or '',
                                            'value': meta_rec.value or '',
                                            'value_type': meta_rec.value_type or ''}))
                                # Update an inventory for product for all
                                # locations
                                for shopify_locations_record in shopify_locations_records:
                                    shopify_location = shopify_locations_record.shopify_location_id
                                    shopify_location_id = shopify_locations_record.id
                                    available_qty = 0
                                    quant_locations = stock_quant_obj.sudo().search([('location_id.usage', '=', 'internal'), (
                                        'product_id', '=', shopify_product_product.product_variant_id.id), ('location_id.shopify_location_ids', 'in', [shopify_location_id])])
                                    for quant_location in quant_locations:
                                        available_qty += quant_location.quantity
                                    location = shopify.InventoryLevel.set(
                                        shopify_location, inventory_item_id, int(available_qty))
            except Exception as e:
                _logger.error(
                    _('Facing a problems while exporting product!: %s') % e)
                s_product_tmpl_id.shopify_error_log = str(e)
            # raise Warning(
            #     _('Facing a problems while exporting product!: %s') % e)

    def export_prod_variant(self, shopify_prod_rec):
        '''
        Process to export product variant from odoo to shopify

        1. Check if product variant already exported or variant has shopify product template.
        2. Set the shopify product variant object and set variant attributes, weight unit, price,
           sku, inventory management, product_id.
        3. If product variant created successfully, then set images and metafields on product variant on
           shopify side. Also update the shopify product variant ID, inventory item ID and Product Template
           ID on shopify product variant one2many.
        4. Update the Inventory of the product variant on respective locations which are mapped with
           shopify locations.
        5. If any issue occurs during the variant export process, then raise the user warnings accordingly.
        '''
        s_prod_tmpl = self.env['shopify.product.template']
        stock_quant_obj = self.env['stock.quant']
        for rec in self:
            rec.test_connection()
            config_id = rec.id
            if shopify_prod_rec.shopify_product_id:
                raise Warning(_('Variant is already exported to Shopify.'))

            variant_val = {}
            product = shopify_prod_rec.product_variant_id
            product_tmpl_id = product.product_tmpl_id
            if product_tmpl_id.sale_ok and product_tmpl_id.purchase_ok:
                s_prod_tmpl_rec = s_prod_tmpl.sudo().search([('product_tmpl_id','=',product_tmpl_id.id),
                    ('shopify_config_id','=',config_id)], limit = 1)
                if not s_prod_tmpl_rec:
                    raise Warning(_('Shopify Product template record is not found. Kindly export a product template'))
                else:
                    shopify_prod_tmpl_id = s_prod_tmpl_rec.shopify_prod_tmpl_id
                    if shopify_prod_tmpl_id:
                        shopify_prod = shopify.Variant()
                        count = 1
                        for value in product.attribute_value_ids:
                            # shopify_prod.'option' + str(count) = value.name
                            opt_cmd = 'shopify_prod.option' + str(count) + " = '" + str(value.name) +"'"
                            exec(opt_cmd)
                            count += 1

                        weight_unit = product.uom_id
                        if weight_unit and weight_unit.name in _shopify_allow_weights:
                            shopify_prod.weight = product.weight
                            shopify_prod.weight_unit = weight_unit.name
                        else:
                            _logger.error(
                                _('UOM is not define for product variant id!: %s') % str(product.id))

                        shopify_prod.price = shopify_prod_rec.lst_price
                        if product.default_code:
                            shopify_prod.sku = product.default_code
                        else:
                            raise ValidationError(_("Please set Internal reference for product variant before exporting to shopify !"))
                        shopify_prod.inventory_management = "shopify"
                        shopify_prod.product_id = shopify_prod_tmpl_id
                        success = shopify_prod.save()
                        if success:
                            variant_id = shopify_prod.id
                            inventory_item_id = shopify_prod.inventory_item_id
                            default_code = shopify_prod.sku
                            product_variant_rec = shopify_prod_rec.product_variant_id
                            if shopify_prod_rec:
                                variant_image = product_variant_rec.image
                                if variant_image:
                                    image = shopify.Image()
                                    image.product_id = shopify_prod_tmpl_id
                                    image.attachment = variant_image.decode("utf-8")
#                                     image.variant_ids = [variant_id]
                                    image.save()
                                    shopify_prod.image_id = image.id
                                    shopify_prod.save()

                                shopify_prod_rec.sudo().update({'shopify_product_id': variant_id,
                                                                'shopify_product_template_id': s_prod_tmpl_rec.id,
                                                                'shopify_inventory_item_id': inventory_item_id,
                                    'last_updated_date':datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT)})
                                shopify_metafields_dict = {}
                                if shopify_prod_rec.meta_fields_ids:
                                    variant_meta_rec = shopify_prod_rec.meta_fields_ids
                                    if variant_meta_rec:
                                        for meta_rec in variant_meta_rec:
                                            shopify_prod.add_metafield(shopify.Metafield({'namespace': meta_rec.namespace or '',
                                                'key': meta_rec.key or '',
                                                'value': meta_rec.value or '',
                                                'value_type': meta_rec.value_type or ''}))
                                shopify_locations_records = self.env['shopify.locations'].sudo().search(
                                    [('shopify_config_id', '=', config_id)])
                                for shopify_locations_record in shopify_locations_records:
                                    shopify_location = shopify_locations_record.shopify_location_id
                                    shopify_location_id = shopify_locations_record.id
                                    available_qty = 0
                                    quant_locations = stock_quant_obj.sudo().search([('location_id.usage', '=', 'internal'), (
                                        'product_id', '=', shopify_prod_rec.product_variant_id.id), ('location_id.shopify_location_ids', 'in', [shopify_location_id])])
                                    for quant_location in quant_locations:
                                        available_qty += quant_location.quantity
                                    location = shopify.InventoryLevel.set(
                                        shopify_location, inventory_item_id, int(available_qty))
                        else:
                            raise Warning(_('Issue raised while exporting product variant!'))
                    else:
                        raise Warning(_('Product template is created at Shopify, but not exported to Shopify. Kindly export a product template'))
            else:
                raise ValidationError(_("A Product should be 'Can be Sold' and 'Can be Purchased' before export"))

    @api.multi
    def update_shopify_inventory(self, shopify_location_id, inventory_item_id, qty):
        """
        Adjust qty on shopify base on given location_id and inventory_item_id
        """
        try:
            self.test_connection()
            adjust_location = shopify.InventoryLevel.adjust(
                shopify_location_id, inventory_item_id, qty)
        except Exception as e:
            _logger.error(
                _('Facing a problems while update a product quantity!: %s') % e)

    @api.multi
    def test_import_orders(self):
        """
        Fetch order ids from shopify with give condition and pass it to import_order function
        """
        self.test_connection()
        shopify_order_id = 1346887714636
#         shopify_orders = shopify.Order.find(
#             status='any', financial_status='paid', fulfillment_status='fulfilled')
#         for shopify_order in shopify_orders:
#             self.import_order(shopify_order.id)
#
#         shopify_orders = shopify.Order.find(
#             status='any', financial_status='partially_refunded', fulfillment_status='partial')
#         for shopify_order in shopify_orders:
#             self.import_order(shopify_order.id)
        order_company = self.sudo().get_shopify_order_company(1360243590988)
#         self.import_order(1706514022485, order_company, True)
        self.sudo(order_company.shopify_user_id.id).import_order(
                            1360243590988, order_company, True)
        # self.import_order(1112794693725)

    def _process_so(self, odoo_so_rec, done_qty_vals = {}):
        """
        Process sale order and return erro_log if any

        1. Set process_order flag True
        2. Confirm a sale order (If get's any issue occurs while confirmation set process_order flag False and update error message error_log)
        3. If porcess_order flag is true then process delivery order. (If any issue occurs while processing delivery order set process_order flag False and update error message error_log)
        4. If porcess_order flag is true and invoice is not created against sale order then process an invoice. (If any issue occurs while processing invoice order set process_order flag False and update error message error_log)
        5. Return an erro_log
        """
        shopify_error_log = ""
        product_moves_done = {}
        process_done = True if done_qty_vals else False
        try:
            process_order = True
            odoo_so_rec.action_confirm()
        except Exception as e:
            shopify_error_log += "\n" if shopify_error_log else ""
            shopify_error_log += "Order confirmation issue"
            if e:
                error_string = "\n" + str(e)
                shopify_error_log += error_string
            process_order = False
            pass

        if process_order:
            try:
                pick_to_backorder = self.env['stock.picking']
                pick_to_do = self.env['stock.picking']
                so_picking_ids = odoo_so_rec.picking_ids
                for picking in so_picking_ids:
                    for move in picking.move_lines:
                        for move_line in move.move_line_ids:
                            if move_line.product_id:
                                if process_done:
                                    if move_line.product_id.id in done_qty_vals.keys():
                                        move_line.qty_done = done_qty_vals[move_line.product_id.id]
                                        del done_qty_vals[move_line.product_id.id]
                                    else:
                                        move_line.qty_done = 0
                                else:
                                    move_line.qty_done = move_line.product_uom_qty
                            else:
                                move_line.qty_done = 0
                    # Done picking with no backorder
                    picking.action_done()
                    backorder_pick = self.env['stock.picking'].sudo().search(
                        [('backorder_id', '=', picking.id)])
                    backorder_pick.action_cancel()

                picking_not_process = so_picking_ids.filtered(lambda picking_id: picking_id.state in ['done', 'cancel'])
                if not picking_not_process:
                    process_order = False
                    shopify_error_log += "\n" if shopify_error_log else ""
                    shopify_error_log += "Order DO processing issue - Picking not found"
            except Exception as e:
                shopify_error_log += "\n" if shopify_error_log else ""
                shopify_error_log += "Order DO processing issue"
                process_order = False
                if e:
                    error_string = "\n" + str(e)
                    shopify_error_log += error_string
                process_order = False
                pass

            if not odoo_so_rec.invoice_ids and process_order:
                try:
                    if odoo_so_rec.shopify_financial_status == 'partially_refunded' and odoo_so_rec.shopify_fulfillment_status == 'partial':
                        #to pass the context if order is partial refunded and partial fulfilled
                        odoo_so_invoice = odoo_so_rec.with_context({'partial_fulfill_refund_order':1}).action_invoice_create()
                    else:
                        odoo_so_invoice = odoo_so_rec.action_invoice_create()
                    invoice = self.env['account.invoice'].browse(
                        odoo_so_invoice[0])
                    invoice.action_invoice_open()
                except Exception as e:
                    shopify_error_log += "\n" if shopify_error_log else ""
                    shopify_error_log += "Order invoice creation and validation issue"
                    if e:
                        error_string = "\n" + str(e)
                        shopify_error_log += error_string
                    process_order = False
                    pass
        return shopify_error_log

    def get_shopify_order_company(self,shopify_order_id):
        _logger.info("Start get_shopify_user_id***********")
        shopify_order = shopify.Order.find(shopify_order_id)
        order_company = self.default_company_id
        shopify_order_attributes = shopify_order.attributes
        shipping_address = shopify_order_attributes.get('shipping_address')
        if shipping_address:
            order_province = shipping_address.province_code
            for company_rec in self.company_ids:
                code = []
                for province in company_rec.shopify_province_ids:
                    code += [province.code]
                if str(order_province) in code:
                    order_company = company_rec
                    break
        _logger.info("End get_shopify_user_id***********")
        return order_company        
        
    
    @api.multi
    def import_order(self, shopify_order_id, order_company, allow_import=False):
        """
        Import provided Sale order id from shopify to odoo

        1. Set shopify_config master's id in shopify_config_id variable
        2. Base on customer province find Company_id
        3. Based on company_id fetch customer_id, warehouse_id, vendor_id and location_id
        4. base on Shopify order fetch financial_status and fulfillment_status
        5. set allow_import flag base on order's financial_status and fulfillment_status
        6. Scrap this step and move it at 11 - Base on order's details fetch fulfillments details
        7. Prepare order_line vals
            7.1 Get product_id of Odoo system base on shopify_product_product master
            7.2 if a product is not found then fetch base on SKU (this is a temporary step, going to scrap once table structure setup well)
            7.3 set price_unit, product_uom_qty base on Shopify line values
            7.4 set product_id and product_uom base on Odoo product recordset
            7.5 If any error occurs while finding a product will log it in shopify_error_log variable
        8. Prepare vals for sale.order master -
            8.1 Set shopify_name, shopify_order_id, shopify_note, shopify_config_id, shopify_fulfillment_status, shopify_financial_status in sale order master as well as set partner_id, company_id, warehouse_id base on company data
            8.2 Add order_line vals in sale order vals
        9. Once sale order vals is prepared, create a sale order in the system. (If any error occurs while processing sale order update it in shopify_error_log variable)
        10. If there is no value in shopify_error_log then base on order's details fetch fulfillments details
        11. Process an individual fulfillment
            11.1 base on fulfillment location and Shopify location of Shopify warehouse identify that fulfillment belongs to same company location's or not
            11.2 If fulfillment belongs to multi-location then create and process PO as well as SO and fulfill a quantity at Shopify stock location
            11.3 If fulfillment belongs to the same company then create an internal transfer and fulfill a quantity at Shopify stock location
        12. Once the quantity is fulfilled at Shopify location - start processing order using process_order function
        13. If any value have shopify_error_log variable then record that error in shopify.order.error.log master
        """
        so_env = self.env['sale.order']
        shopify_order_id = int(shopify_order_id)
        if so_env.sudo().search_count([('shopify_order_id', '=', shopify_order_id)]) > 0:
            return True
        
        shopify_order = shopify.Order.find(shopify_order_id)
        # base on Shopify order fetch financial_status and fulfillment_status
        financial_status = shopify_order.financial_status
        fulfillment_status = shopify_order.fulfillment_status

        # set allow_import flag base on order's financial_status and
        # fulfillment_status
        if not allow_import:
            if financial_status == 'partially_refunded' and fulfillment_status == 'partial':
                allow_import = True
            elif financial_status == 'paid' and fulfillment_status == 'fulfilled':
                allow_import = True

        if allow_import:
            shopify_error_log = ''
            odoo_so_id = ''
            shopify_config_id = self.id

            product_env = self.env['shopify.product.product']
            product_variant_env = self.env['product.product']
            tax_env = self.env['account.tax']
            po_env = self.env['purchase.order']
            shopify_location_obj = self.env['shopify.locations']
            stock_location_obj = self.env['stock.location']
            partner_obj = self.env['res.partner']
            province_obj = self.env['res.country.state']

            shopify_order_attributes = shopify_order.attributes
            shipping_address = shopify_order_attributes.get('shipping_address')
            shopify_customer_id = ''
            shopify_vendor_id = ''
            order_province_id = ''
            order_province = ''
            shopify_vendor_rec = ''
            if shipping_address:
                order_province = shipping_address.province_code

            # Based on company_id fetch customer_id, warehouse_id, vendor_id and
            # location_id
            company_id = order_company.id
            if order_province:
                if order_company.country_id:
                    domain = [('code','=',order_province),('country_id','=', order_company.country_id.id)]
                else:
                    domain = [('code','=',order_province)]
                order_province_id = province_obj.search(domain, limit=1)
            #Chcek customer is created for that provience and commpany
            if order_province_id:
                shopify_partner_records = partner_obj.sudo().search([('company_id','=',company_id),
                    ('is_shopify','=',True), ('state_id','=',order_province_id.id)])
                for shopify_partner_rec in shopify_partner_records:
                    if shopify_partner_rec.customer == True:
                        shopify_customer_id = shopify_partner_rec.id
                    if shopify_partner_rec.supplier == True:
                        shopify_vendor_id = shopify_partner_rec.id
            if not shopify_customer_id:
                shopify_customer_id = order_company.shopify_customer_id.id

            if not shopify_vendor_id:
                shopify_vendor_rec = order_company.shopify_vendor_id
                if shopify_vendor_rec:
                    shopify_vendor_id = shopify_vendor_rec.id

            shopify_warehouse_id = order_company.shopify_warehouse_id.id
            shopify_location_rec = order_company.shopify_location_id
            shopify_location_id = shopify_location_rec.id
            shopify_user_id = order_company.shopify_user_id.id

            # Scrap this step and move it at 11 - Base on order's details fetch fulfillments details
            # fulfillments = shopify.Fulfillment.find(order_id=shopify_order.id)

            # Prepare order_line vals
            line_vals = []
            subtotal = 0
            for line_item in shopify_order.line_items:
                line_data = line_item.attributes
                # Get product_id of Odoo system base on shopify_product_product
                # master
                product = product_env.sudo(shopify_user_id).search([('shopify_product_id', '=', line_data.get(
                    'variant_id'))], limit=1).product_variant_id
                if not product:
                    # if a product is not found then fetch base on SKU (this is
                    # a temporary step, going to scrap once table structure
                    # setup well)
                    product = product_variant_env.sudo(shopify_user_id).search(
                        [('default_code', '=', line_data.get('sku'))], limit=1)
                if product:
                    # Add Tax
                    # shopify_tax = False
                    # tax_ids = []
                    # for tax_line in line_data.get('tax_lines'):
                    #     tax_calc = tax_line.attributes.get('rate') * 100
                    #     tax = "Shopify Tax " + str(tax_calc) + " %"
                    #     shopify_tax = tax_env.search([('name', '=', tax)])
                    #     if not shopify_tax:
                    #         shopify_tax = tax_env.create(
                    #             {'name': tax, 'amount': float(tax_calc)})
                    #     tax_ids.append(shopify_tax[0].id)

                    # set price_unit, product_uom_qty base on Shopify line values
                    # set product_id and product_uom base on Odoo product recordset
                    # If any error occurs while finding a product will log it
                    # in shopify_error_log variable
                    line_price_unit = float(line_data.get('price'))
                    line_data_quantity = line_data.get('quantity')
                    if line_data.get('total_discount') and line_data.get('quantity') > 0:
                        line_price_unit = line_price_unit - (float(line_data.get('total_discount'))/line_data.get('quantity') or 0)
                    subtotal += line_price_unit * line_data_quantity
                    line_vals_dict = {'product_id': product.id,
                                      'name': line_data.get('name').encode('utf-8'),
                                      'price_unit': line_price_unit,
                                      'product_uom_qty': line_data_quantity,
                                      'product_uom': product.uom_id.id,
                                      # 'tax_id': shopify_tax and [(6, 0, tax_ids)] or
                                      # [(6, 0, [])]
                                      }
                    line_vals.append((0, 0, line_vals_dict))
#                     line_vals.extend([(0, 0, line_vals_dict)])
                    
                else:
                    shopify_error_log += "\n" if shopify_error_log else ""
                    shopify_error_log += "Product does not exist"
            #Prepare vals for shiping lines
            shipping_product = product_variant_env.sudo(shopify_user_id).search([('type', '=', 'service'), ('shopify_shipping_product','=',True)], limit=1)
            for shipping_line in shopify_order.shipping_lines:
                shipping_line_data = shipping_line.attributes
                line_prod_name = shipping_line_data.get('title').encode('utf-8')
                if shipping_line_data.get('handle'):
                    handle_str = " / " + shipping_line_data.get('handle').encode('utf-8')
                    line_prod_name += handle_str
                line_prod_price = shipping_line_data.get('price') or 0
                if shipping_product:
                    line_vals_dict = {'product_id': shipping_product.id,
                    'name': line_prod_name,
                    'price_unit': line_prod_price,
                    'product_uom_qty': 1,
                    'product_uom': shipping_product.uom_id.id,
                    # 'tax_id': [(6, 0, [])]
                    }
                    line_vals.append((0, 0, line_vals_dict))
                else:
                    shopify_error_log += "\n" if shopify_error_log else ""
                    shopify_error_log += "Shipping product does not exist in odoo system"
            #Prepare vals to add discount product
            for app in shopify_order.discount_applications:
                allocation_method = app.allocation_method
                target_selection = app.target_selection
                target_type = app.target_type
                value_type = app.value_type
                discount = float(app.value)
                # if target_selection == 'all' and allocation_method == 'across':
                discount_product = product_variant_env.sudo(shopify_user_id).search([('type', '=', 'service'), ('shopify_discount_product','=',True)], limit=1)
                if discount_product:
                    if target_type == 'line_item' and target_selection == 'all' and allocation_method == 'across':
                        if value_type == 'fixed_amount':
                            if subtotal <= discount:
#                                 discount = subtotal
                                temp_line_vals = []
                                for k,v,d in line_vals:
                                    if shipping_product and d.get('product_id') and d.get('product_id') != shipping_product.id:
                                        d.update({'discount': 100})
                                        temp_line_vals.append((0,0,d))
                                    else:
                                        temp_line_vals.append((0,0,d))
                                if temp_line_vals:
                                    line_vals = temp_line_vals
                            else:
                                line_vals_dict = {'product_id': discount_product.id,
                                'name': value_type,
                                'price_unit': -(discount),
                                'product_uom_qty': 1,
                                'product_uom': discount_product.uom_id.id,
                                }
                                line_vals.append((0, 0, line_vals_dict))
                        elif value_type == 'percentage':
                            final_discount = (subtotal * discount)/100
                            final_discount = str(final_discount)
                            final_discount_split_list = final_discount.split(".")
                            final_discount = final_discount_split_list[0] + "." + final_discount_split_list[1][:2]
                            final_discount = float(final_discount)
                            if subtotal <= final_discount:
#                                 final_discount = subtotal
                                temp_line_vals = []
                                for k,v,d in line_vals:
                                    if shipping_product and d.get('product_id') and d.get('product_id') != shipping_product.id:
                                        d.update({'discount': 100})
                                        temp_line_vals.append((0,0,d))
                                    else:
                                        temp_line_vals.append((0,0,d))
                                if temp_line_vals:
                                    line_vals = temp_line_vals
                            else:
                                line_vals_dict = {'product_id': discount_product.id,
                                'name': value_type,
                                'price_unit': -(final_discount),
                                'product_uom_qty': 1,
                                'product_uom': discount_product.uom_id.id,
                                }
                                line_vals.append((0, 0, line_vals_dict))
                    elif target_type == 'shipping_line' and shipping_product:
                        shipping_product_id = shipping_product.id
                        if value_type == 'fixed_amount':
                            temp_shipping_line_vals = []
                            for k,v,d in line_vals:
                                if d['product_id'] == shipping_product_id:
                                    d['price_unit'] = discount
                                temp_shipping_line_vals.append((0,0,d))
                            if temp_shipping_line_vals:
                                line_vals = temp_shipping_line_vals
                        elif value_type == 'percentage':
                            temp_shipping_line_vals = []
                            for k,v,d in line_vals:
                                if d['product_id'] == shipping_product_id:
                                    d['discount'] = discount
                                temp_shipping_line_vals.append((0,0,d))
                            if temp_shipping_line_vals:
                                line_vals = temp_shipping_line_vals
                # else:
                #     shopify_error_log += "\n" if shopify_error_log else ""
                #     shopify_error_log += "Discount product does not exist in odoo system"

            # Prepare vals for sale.order master
            so_vals = {'partner_id': shopify_customer_id,
                       'company_id': company_id,
                       'warehouse_id': shopify_warehouse_id,
                       'order_line': line_vals,
                       'shopify_name': str(shopify_order.order_number) or '',
                       'shopify_order_id': str(shopify_order.id) or '',
                       'shopify_note': shopify_order.note or '',
                       'shopify_config_id': shopify_config_id,
                       'shopify_fulfillment_status': fulfillment_status,
                       'shopify_financial_status': financial_status,
                       'user_id':shopify_user_id,
                       }

            # Once sale order vals is prepared, create a sale order in the
            # system. (If any error occurs while processing sale order update
            # it in shopify_error_log variable)
            try:
                odoo_so_rec = so_env.create(so_vals)
            except Exception as e:
                shopify_error_log += "\n" if shopify_error_log else ""
                shopify_error_log += "Order creation issue"
                if e:
                    error_string = "\n" + str(e)
                    shopify_error_log += error_string
                pass

            # Now process picking
            # try:
            if not shopify_error_log and odoo_so_rec:
                # If there is no value in shopify_error_log then base on
                # order's details fetch fulfillments details
                fulfillments = shopify.Fulfillment.find(
                    order_id=shopify_order.id, status='success')
                odoo_so_id = odoo_so_rec.id
                odoo_so_name = odoo_so_rec.name or ''
                # product_moves_done = {}
                po_vals_list = []
                done_qty_vals = {}
                src_shopify_customer_id = ''
                src_shopify_warehouse_id = ''
                src_shopify_location_rec = ''
                multi_location_company = ''
                src_shopify_user_id = ''
                odoo_po_rec = po_env.sudo(shopify_user_id).search([('company_id', '=', company_id), ('partner_id', '=', shopify_vendor_id), ('origin', '=', odoo_so_name)], limit=1)
                po_vals = {}
                if not odoo_po_rec:
                    fpos = self.env['account.fiscal.position'].with_context(force_company=company_id).get_fiscal_position(shopify_vendor_id)
                    po_currency_id = shopify_vendor_rec.with_context(force_company=company_id).property_purchase_currency_id.id or self.env.user.company_id.currency_id.id
                    po_payment_term_id = shopify_vendor_rec.with_context(force_company=company_id).property_supplier_payment_term_id.id
                    po_vals = {'partner_id': shopify_vendor_id,
                               'company_id': company_id,
                               'fiscal_position_id': fpos,
                               'currency_id': po_currency_id,
                               'payment_term_id': po_payment_term_id,           
                               'origin': odoo_so_name,                               
                               }

                    vendor_picking_type_rec = self.env['stock.picking.type'].sudo(shopify_user_id).search(
                        [('warehouse_id', '=', shopify_warehouse_id), ('code', '=', 'incoming')], limit=1)
                    if vendor_picking_type_rec:
                        po_vals.update({'picking_type_id': vendor_picking_type_rec.id})


                # Process an individual fulfillment
                for fulfillment in fulfillments:
                    location_id = fulfillment.location_id
                    if location_id:
                        # base on fulfillment location and Shopify location of Shopify warehouse identify that fulfillment belongs to same company location's or not
                        # If fulfillment belongs to multi-location then create and process PO as well as SO and fulfill a quantity at Shopify stock location
                        # If fulfillment belongs to the same company then
                        # create an internal transfer and fulfill a quantity at
                        # Shopify stock location
                        s_location_id = self.env['shopify.locations'].sudo().search([('shopify_location_id', '=', str(
                            location_id)), ('shopify_config_id', '=', shopify_config_id)], limit=1)
                        if s_location_id:
                            src_location_rec = self.env['stock.location'].sudo().search(
                                [('shopify_location_ids', '=', s_location_id.id)], limit=1)
                            if src_location_rec and shopify_location_id:
                                src_location_company_rec = src_location_rec.company_id
                                src_location_company = src_location_company_rec.id if src_location_company_rec else ''
                                shopify_location_company = shopify_location_rec.company_id.id if shopify_location_rec.company_id else ''
                                if src_location_company and shopify_location_company and shopify_location_company != src_location_company:
                                    multi_comp = True
                                    if src_location_company_rec.shopify_intercompany_customer_id:
                                        src_shopify_customer_id = src_location_company_rec.shopify_intercompany_customer_id.id
                                    else:
                                        src_shopify_customer_id = src_location_company_rec.shopify_customer_id.id
#                                     src_shopify_warehouse_id = src_location_rec.m_warehouse_id.id or src_location_rec.get_warehouse().id
                                    src_shopify_warehouse_id = src_location_company_rec.shopify_warehouse_id.id
                                    src_shopify_location_rec = src_location_company_rec.shopify_location_id
                                    multi_location_company = src_location_company
                                    src_shopify_user_id = src_location_company_rec.shopify_user_id.id
                                else:
                                    multi_comp = False

                                if multi_comp:
                                    done_qty_vals,shopify_error_log = self.sudo()._process_internal_transfer(
                                        shopify_warehouse_id, src_location_rec, src_shopify_location_rec,
                                        odoo_so_name, fulfillment, src_location_company, done_qty_vals, shopify_error_log)

                                    if 'picking_type_id' in po_vals:
                                        po_lines_vals = []
                                        for line_item in fulfillment.line_items:
                                            line_data = line_item.attributes
                                            product = product_env.sudo(shopify_user_id).search(
                                                [('shopify_product_id', '=', line_data.get('variant_id'))]).product_variant_id
                                            if not product:
                                                product = product_variant_env.sudo(shopify_user_id).search(
                                                    [('default_code', '=', line_data.get('sku'))])
                                            if product:
                                                today_date = datetime.today().date().strftime(DEFAULT_SERVER_DATE_FORMAT)
                                                prod_seller_ids = product.seller_ids
                                                vendors = prod_seller_ids.filtered(lambda v: (v.name.id == shopify_vendor_id and v.product_id.id == product.id and v.date_start and v.date_start <= today_date and v.date_end and v.date_end >= today_date))
                                                if not vendors:
                                                    vendors = prod_seller_ids.filtered(lambda v: (v.name.id == shopify_vendor_id and not v.product_id.id and v.date_start and v.date_start <= today_date and v.date_end and v.date_end >= today_date))
                                                    if not vendors:
                                                        vendors = prod_seller_ids.filtered(lambda v: (v.name.id == shopify_vendor_id and v.product_id.id == product.id))
                                                        if not vendors:
                                                            vendors = prod_seller_ids.filtered(lambda v: v.name.id == shopify_vendor_id and not v.product_id.id)
                                                if vendors:
                                                    for vendor in vendors:
                                                        price_unit = vendor.price
                                                        if price_unit > 0:
                                                            break
                                                else:
                                                    price_unit = product.standard_price
                                                product_id = product.id
                                                product_name = product.name or ''
                                                qty_move = line_data.get('quantity')
                                                po_lines_vals.append((0, 0, {
                                                    'name': product_name,
                                                    'product_id': product_id,
                                                    'product_qty': qty_move,
                                                    'product_uom': product.uom_po_id.id,
                                                    'print_qty': qty_move,
                                                    'price_unit': price_unit,
                                                    'date_planned': datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                                                }))
                                            else:
                                                shopify_error_log += "\n" if shopify_error_log else ""
                                                shopify_error_log += "Product does not exist"
                                        process_po = True
                                        po_vals_list.append(po_vals)
                                        try:
                                            if odoo_po_rec:
                                                odoo_po_rec.write({'order_line': po_lines_vals})
                                            else:
                                                po_vals.update({'order_line': po_lines_vals})
                                                odoo_po_rec = po_env.sudo(shopify_user_id).create(po_vals)

                                        except Exception as e:
                                            shopify_error_log += "\n" if shopify_error_log else ""
                                            shopify_error_log += "Purchase order creation issue - " + \
                                                str(e)
                                            process_po = False
                                            pass

                                    # for po_vals_l in po_vals_list[0]:
                                    # po_rec = po_env.sudo(shopify_user_id).search([('company_id', '=', company_id),
                                    #     ('partner_id', '=', shopify_vendor_id),
                                    #     ('origin', '=', odoo_so_name)], limit=1)
                                    # if po_rec:
                                    #     po_rec.sudo(shopify_user_id).button_confirm()
                                    #     for picking in po_rec.picking_ids:
                                    #         for move in picking.move_lines:
                                    #             move.update({'quantity_done': move.product_uom_qty})
                                    #         picking.action_done()
                                else:
                                    done_qty_vals,shopify_error_log = self.sudo()._process_internal_transfer(
                                        shopify_warehouse_id, src_location_rec, shopify_location_rec, odoo_so_name, fulfillment, company_id, done_qty_vals, shopify_error_log)

                # po_rec = po_env.sudo(shopify_user_id).search([('company_id', '=', company_id),
                #                             ('partner_id', '=', shopify_vendor_id),
                #                             ('origin', '=', odoo_so_name)], limit=1)
                if odoo_po_rec:
                    po_order_line_rec = odoo_po_rec.order_line.filtered(lambda line: line.price_unit == 0)
                    odoo_po_rec.sudo(shopify_user_id).button_confirm()
                    if not po_order_line_rec:
                        # forcefully calculate price unit according to quantity of the product
                        for po_line in odoo_po_rec.order_line:
                            po_line._onchange_quantity()
                        po_order_line_rec = odoo_po_rec.order_line.filtered(lambda line: line.price_unit == 0)
                    if not po_order_line_rec:
                        try:
                            for picking in odoo_po_rec.picking_ids:
                                for move in picking.move_lines:
                                    move.update({'quantity_done': move.product_uom_qty})
                                picking.action_done()
                        except Exception as e:
                            shopify_error_log += "\n" if shopify_error_log else ""
                            shopify_error_log += "Picking done creation issue"
                            if e:
                                error_string = "\n" + str(e)
                                shopify_error_log += error_string
                            pass
                        #to do : - Process vendor bill for this PO. Create a vendor bill and process to Validate.
                        po_partner_rec = odoo_po_rec.partner_id
                        odoo_po_rec.order_line._compute_tax_id()
                        odoo_po_rec.order_line._compute_amount()
                        src_vb_vals = {'partner_id': po_partner_rec.id,
                                        'purchase_id': odoo_po_rec.id,
                                        'account_id': po_partner_rec.property_account_payable_id.id,
                                        'type': 'in_invoice',
                                       }
                        try:
                            src_vendor_bill_rec = self.env['account.invoice'].sudo(shopify_user_id).create(
                                src_vb_vals)
                            src_vendor_bill_rec.sudo(shopify_user_id).purchase_order_change()
                            src_vendor_bill_rec._onchange_invoice_line_ids()
                            src_vendor_bill_rec.sudo(shopify_user_id).action_invoice_open()

                        except Exception as e:
                            shopify_error_log += "\n" if shopify_error_log else ""
                            shopify_error_log += "Vendor Bill creation issue"
                            if e:
                                error_string = "\n" + str(e)
                                shopify_error_log += error_string
                            pass

                        so_line_vals = []
                        for vb in odoo_po_rec.order_line:
                            prod_id = vb.product_id
                            so_line_vals.append((0,0,{'product_id': prod_id.id,
                                                      'price_unit': vb.price_unit,
                                                      'product_uom_qty': vb.product_qty,
                                                      'product_uom': prod_id.uom_id.id}))
                        if so_line_vals:
                            shopify_note = "Order is created from purchase order reference "+odoo_po_rec.name
                            src_so_vals = {'partner_id': src_shopify_customer_id,
                                           'company_id': multi_location_company,
                                           'warehouse_id': src_shopify_warehouse_id,
                                           'order_line': so_line_vals,
                                           'origin': odoo_so_name + ' / ' + odoo_po_rec.name,
                                           'shopify_name':  str(shopify_order.order_number) or '',
                                           'shopify_order_id': str(shopify_order.id) or '',
                                           'shopify_note': shopify_note,
                                           'shopify_config_id': shopify_config_id,
                                           'user_id':src_shopify_user_id,
                                           # 'shopify_fulfillment_status': fulfillment_status,
                                           # 'shopify_financial_status': financial_status,
                                           }

                            # Process Multi company Orders
                            try:
                                src_so_rec = so_env.sudo(src_shopify_user_id).create(src_so_vals)
                            except Exception as e:
                                shopify_error_log += "\n" if shopify_error_log else ""
                                shopify_error_log += "Other company Order creation issue"
                                if e:
                                    error_string = "\n" + str(e)
                                    shopify_error_log += error_string
                                pass

                            try:
                                shopify_error_log += self.sudo(src_shopify_user_id)._process_so(src_so_rec)
                            except Exception as e:
                                shopify_error_log += "\n" if shopify_error_log else ""
                                shopify_error_log += "Other company order process issue"
                                if e:
                                    error_string = "\n" + str(e)
                                    shopify_error_log += error_string
                                pass
                    else:
                        shopify_error_log += "Purchase Order #"+odoo_po_rec.name+" Purchase order lines are having zero price unit for some of their products. "

                # Once the quantity is fulfilled at Shopify location - start
                # processing order using process_order function
                try:
                    shopify_error_log += self.sudo(shopify_user_id)._process_so(odoo_so_rec,done_qty_vals)
                except Exception as e:
                    shopify_error_log += "\n" if shopify_error_log else ""
                    shopify_error_log += "Main order process issue"
                    if e:
                        error_string = "\n" + str(e)
                        shopify_error_log += error_string
                    pass

            # If any value have shopify_error_log variable then record that error
            # in shopify.order.error.log master
            if shopify_error_log:
                self.env['shopify.order.error.log'].create({
                    'error': shopify_error_log,
                    'shopify_config_id': shopify_config_id,
                    'company_id': company_id,
                    'date': fields.Date.today(),
                    'shopify_so_id': str(shopify_order.id) or '',
                    'odoo_so_id': odoo_so_id,
                })

    def _process_internal_transfer(self, warehouse_id, location_id, location_dest_id, odoo_so_name, fulfillment, company_id, done_qty_vals, shopify_error_log):
        """
        Transfer a product inventory from one location to another
        1. search picking_type record using warehouse
        2. Create a record for transfer
        3. validate a transfer
        4. if any error occurs during all these steps will log it into shopify_error_log variable
        5. return shopify_error_log
        """
        picking_type_rec = self.env['stock.picking.type'].sudo().search(
            [('warehouse_id', '=', warehouse_id),
             ('code', '=', 'internal')], limit=1)
        if picking_type_rec:
            product_env = self.env['shopify.product.product']
            product_variant_env = self.env['product.product']
            move_lines_vals = []
            for line_item in fulfillment.line_items:
                line_data = line_item.attributes
                product = product_env.search(
                    [('shopify_product_id', '=', line_data.get('variant_id'))]).product_variant_id
                if not product:
                    product = product_variant_env.search(
                        [('default_code', '=', line_data.get('sku'))])

                if product:
                    product_id = product.id
                    qty_move = line_data.get('quantity')
                    if product_id in done_qty_vals.keys():
                        d_qty = done_qty_vals[product_id]
                        done_qty_vals.update({product_id: d_qty + qty_move})
                    else:
                        done_qty_vals.update({product_id : qty_move})

                    move_lines_vals.append((0, 0, {'product_id': product_id,
                                                   'quantity_done': qty_move,
                                                   'product_uom_qty': qty_move,
                                                   'location_id': location_id.id,
                                                   'location_dest_id': location_dest_id.id,
                                                   'product_uom': product.uom_id.id,
                                                   'name': location_id.name}))
                else:
                    shopify_error_log += "\n" if shopify_error_log else ""
                    shopify_error_log += "Product does not exist"
            sp_vals = {'location_id': location_id.id,
                       'location_dest_id': location_dest_id.id,
                       'picking_type_id': picking_type_rec.id,
                       'move_lines': move_lines_vals,
                       'company_id': company_id,
                       'origin': odoo_so_name,
                       }
            sp_id = self.env['stock.picking'].sudo().create(sp_vals)
            sp_id.with_context(shopify_picking_validate=True).button_validate()
        else:
            shopify_error_log += "\n" if shopify_error_log else ""
            shopify_error_log += "Picking type not found for warehouse id - " + \
                str(warehouse_id)
        return done_qty_vals,shopify_error_log
