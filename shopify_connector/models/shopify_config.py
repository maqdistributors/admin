# -*- coding: utf-8 -*-

import shopify
import logging


from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

from odoo import models, fields, api, _
from odoo.exceptions import Warning, ValidationError

_logger = logging.getLogger(__name__)
_shopify_allow_weights = ['kg','lb','oz','g']

class ShopifyConfig(models.Model):

    _name = 'shopify.config'
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
        res = super(ShopifyConfig, self).create(vals)
        company_ids = vals['company_ids'][0][2]
        default_company_id = vals['default_company_id']
        if default_company_id not in company_ids:
            raise ValidationError(
                _("The chosen default company is not in the companies !"))
        return res

    @api.multi
    def write(self, vals):
        res = super(ShopifyConfig, self).write(vals)
        default_company_id = vals.get(
            'default_company_id') or self.default_company_id.id
        if default_company_id not in self.company_ids.ids:
            raise ValidationError(
                _("The chosen default company is not in the companies !"))
        return res

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
        product_tmpl_ids = self.env['shopify.product.template'].sudo().search(
            [('shopify_config_id', '=', self.id), ('shopify_prod_tmpl_id', 'in', ['',False])])
#         product_tmpl_ids = [44038]
        return self.export_product(product_tmpl_ids)

    @api.multi
    def export_product(self, s_product_tmpl_ids):
        """
        process product_tmpl_ids and pass it to the shopify
        """
        self.check_connection()

        product_tmpl_obj = self.env['product.template']
        shopify_prod_obj = self.env['shopify.product.product']
        stock_quant_obj = self.env['stock.quant']
        shopify_config_id = self.id
        shopify_locations_records = self.env['shopify.locations'].sudo().search(
            [('shopify_config_id', '=', shopify_config_id)])
        print("shopify_locations_records --->>", shopify_locations_records)

        for s_product_tmpl_id in s_product_tmpl_ids:
            print("s_product_tmpl_id --->>", s_product_tmpl_id)
            try:
                product_tmpl_id = s_product_tmpl_id.product_tmpl_id
                products = shopify_prod_obj.sudo().\
                    search([('shopify_config_id', '=', shopify_config_id),
                            ('shopify_product_id', 'in', ['', False]),
                            ('product_variant_id', 'in', product_tmpl_id.product_variant_ids.ids)])
                print("products --->>", products)
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

                variants = []
                for s_product in products:
                    variant_val = {}
                    product = s_product.product_variant_id

                    count = 1
                    print("product.attribute_value_ids",
                          product.attribute_value_ids)
                    for value in product.attribute_value_ids:
                        variant_val.update({'option' + str(count): value.name})
                        count += 1

                    # lst_price = s_product.lst_price if s_product.lst_price > 0 else product.lst_price

                    weight_unit = product.uom_id
                    if weight_unit and weight_unit.name in _shopify_allow_weights:
                        variant_val.update({'weight': product.weight,
                                            'weight_unit': weight_unit.name})
                    else:
                        _logger.error(_('UOM is not define for product variant id!: %s') % str(product.id))

                    variant_val.update(
                        {'price': s_product.lst_price,
                         'sku': product.default_code or product.id,
                         "inventory_management": "shopify"})
                    variants += [variant_val]

                images = []
                if product_tmpl_id.image_medium:
                    images += [{'attachment': product_tmpl_id.image_medium}]
                for product_image in product_tmpl_id.product_image_ids:
                    if product_image.image:
                        images += [{'attachment': product_image.image}]

                prod_tags = product_tmpl_id.prod_tags_ids
                province_tags = product_tmpl_id.province_tags_ids
                str_prod_province_tags = []
                for prod_tag in prod_tags:
                    str_prod_province_tags.append(prod_tag.name)
                for prov_tag in province_tags:
                    str_prod_province_tags.append(prov_tag.name)
                tags = ",".join(str_prod_province_tags)

                new_product = shopify.Product()
                new_product.title = product_tmpl_id.name
                if s_product_tmpl_id.product_type:
                    new_product.product_type = s_product_tmpl_id.product_type.name  # "Snowboard"
                if s_product_tmpl_id.vendor:
                    new_product.vendor = s_product_tmpl_id.vendor.name  # "Burton"
                if tags:
                    new_product.tags = tags  # "Barnes & Noble, John's Fav, \"Big Air\""
                if s_product_tmpl_id.body_html:
                    new_product.body_html = str(s_product_tmpl_id.body_html)
                if options:
                    new_product.options = options
                if variants:
                    new_product.variants = variants
                if images:
                    new_product.images = images
                success = new_product.save()  # returns false if the record is invalid
                if success:
                    s_product_tmpl_id.update({'shopify_published': True})
                    shopify_product_tmpl_id = new_product.id
                    if shopify_product_tmpl_id:
                        s_product_tmpl_id.update(
                            {'shopify_prod_tmpl_id': shopify_product_tmpl_id})
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
                            if product_variant_rec:
                                variant_image = product_variant_rec.image_medium
                                if variant_image:
                                    image = shopify.Image(
                                        {'product_id': shopify_product_tmpl_id})
                                    image.attachment = variant_image
                                    image.variant_ids = [variant_id]
                                    image.save()
                            if shopify_product_product:
                                shopify_product_product.sudo().update({'shopify_product_id': variant_id,
                                                                       'shopify_product_template_id': s_product_tmpl_id.id,
                                                                       'shopify_inventory_item_id': inventory_item_id})

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

    @api.multi
    def update_shopify_inventory(self, shopify_location_id, inventory_item_id, qty):
        """
        On stock move done this function is adjust qty on shopify
        """
        try:
            self.check_connection()
            adjust_location = shopify.InventoryLevel.adjust(
                shopify_location_id, inventory_item_id, qty)
        except Exception as e:
            _logger.error(
                _('Facing a problems while update a product quantity!: %s') % e)
            # raise Warning(
            # _('Facing a problems while update a product quantity!: %s') % e)

#     @api.multi
#     def import_locations(self):
#         """
#         This is a test function. No need to do anything as locations are configured by client
#         """
#         self.check_connection()
#         locations = shopify.Location.find()
#         print("locations*******", locations)
#         for location in locations:
#             country_code = location.country_code
#             country_id = self.env['res.country'].sudo().search(
#                 [('code', '=', country_code)])
#             country_name = country_id.name if country_id else ''
#             self.env['shopify.locations'].create({
#                 'active': location.active,
#                 'address1': location.address1,
#                 'address2': location.address2,
#                 'city': location.city,
#                 'country_code': country_code,
#                 'name': location.name,
#                 'phone': location.phone,
#                 'province_code': location.province_code,
#                 'zip': location.zip,
#                 'legacy': location.legacy,
#                 'shopify_location_id': location.id,
#                 'shopify_config_id': self.id,
#                 'country_name': country_name,
#                 'province': location.province,
#                 'updated_at_shopify': location.updated_at,
#                 'created_at_shopify': location.created_at})
# 
    @api.multi
    def import_orders(self):
        self.check_connection()
        shopify_orders = shopify.Order.find(
            status='any', financial_status='paid', fulfillment_status='fulfilled')
        print("shopify fulfilled orders**********", shopify_orders)
        for shopify_order in shopify_orders:
            self.import_order(shopify_order.id)

        shopify_orders = shopify.Order.find(
            status='any', financial_status='partially_refunded', fulfillment_status='partial')
        print("shopify partial fulfilled orders**********", shopify_orders)
        for shopify_order in shopify_orders:
            self.import_order(shopify_order.id)
        # self.import_order(1152736167756)
        # self.import_order(1112794693725)

    def _process_so(self,odoo_so_rec):
        shopify_error_log = ""
        product_moves_done = {}
        try:
            process_order = True
            odoo_so_rec.action_confirm()
        except:
            shopify_error_log += "\n" if shopify_error_log else ""
            shopify_error_log += "Order confirmation issue"
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
                            if move_line.product_id.id in product_moves_done.keys():
                                move_line.quantity_done = product_moves_done[
                                    move_line.product_id.id]
                                move_line.qty_done = product_moves_done[
                                    move_line.product_id.id]
                            else:
                                move_line.quantity_done = 0
                                move_line.qty_done = 0
                    # Done picking with no backorder
                    picking.action_done()
                    backorder_pick = self.env['stock.picking'].search(
                        [('backorder_id', '=', picking.id)])
                    backorder_pick.action_cancel()

                picking_not_process = so_picking_ids.filtered(lambda picking_id: picking_id.state in ['done','cancel'])
                if not picking_not_process:
                    process_order = False
                    shopify_error_log += "\n" if shopify_error_log else ""
                    shopify_error_log += "Order DO processing issue"
            except:
                shopify_error_log += "\n" if shopify_error_log else ""
                shopify_error_log += "Order DO processing issue"
                process_order = False
                pass
            if not odoo_so_rec.invoice_ids and process_order:
                try:
                    odoo_so_invoice = odoo_so_rec.action_invoice_create()
                    invoice = self.env['account.invoice'].browse(
                        odoo_so_invoice[0])
                    invoice.action_invoice_open()
                except:
                    shopify_error_log += "\n" if shopify_error_log else ""
                    shopify_error_log += "Order invoice creation and validation issue"
                    pass
        return shopify_error_log

    @api.multi
    def import_order(self, shopify_order_id):
        """
        This is a test function. No need to do anything as locations are configured by client
        """
        shopify_error_log = ''
        odoo_so_id = ''

        # try:
        # self.check_connection()
        # except:
        #     shopify_error_log += 'Connection issue'
        shopify_config_id = self.id

        so_env = self.env['sale.order']
        product_env = self.env['shopify.product.product']
        product_variant_env = self.env['product.product']
        tax_env = self.env['account.tax']
        po_env =  self.env['purchase.order']
        shopify_location_obj = self.env['shopify.locations']
        stock_location_obj = self.env['stock.location']

        # if so_env.sudo().search_count([('shopify_order_id', '=', shopify_order_id)]) > 0:
        #     return True
        shopify_order_id = int(shopify_order_id)
        shopify_order = shopify.Order.find(shopify_order_id)
        # print("Shopify Order Id",shopify_order)

        # Base on customer provience find Company_id
        order_company = self.default_company_id
        shopify_order_attributes = shopify_order.attributes
        shipping_address = shopify_order_attributes.get('shipping_address')
        if shipping_address:
            order_province = shipping_address.province_code
            # print("order_province***", order_province)
            for company_rec in self.company_ids:
                code = []
                for province in company_rec.shopify_province_ids:
                    code += [province.code]
                if str(order_province) in code:
                    order_company = company_rec
                    break
        company_id = order_company.id
        shopify_customer_id = order_company.shopify_customer_id.id
        shopify_warehouse_id = order_company.shopify_warehouse_id.id
        shopify_vendor_id = order_company.shopify_vendor_id.id
        shopify_location_rec = order_company.shopify_location_id
        shopify_location_id = shopify_location_rec.id

        financial_status = shopify_order.financial_status
        fulfillment_status = shopify_order.fulfillment_status

        if financial_status == 'partially_refunded' and fulfillment_status == 'partial':
            allow_import = True
        elif financial_status == 'paid' and fulfillment_status == 'fulfilled':
            allow_import = True
        else:
            allow_import = False

        if allow_import:
            fulfillments = shopify.Fulfillment.find(order_id=shopify_order.id)

            # TODO: Base on customer provience find warehouse, customer id and
            # company_id
            line_vals = []
            for line_item in shopify_order.line_items:
                line_data = line_item.attributes
                product = product_env.search(
                    [('shopify_product_id', '=', line_data.get('variant_id'))], limit=1).product_variant_id
                if not product:
                    product = product_variant_env.search(
                        [('default_code', '=', line_data.get('sku'))], limit=1)
                # TODO: When we import a product from shopify then we need to check weather product is imported or not
                # if not imported ten we need to import it first before oreder creation
                # if not product:
                #     self.import_product_product()
                #     product = product_env.search(
                #     [('product_sfy_variant_id', '=', line_data.get('variant_id'))])
                #   new_cr.commit()
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
                    line_vals.append((0, 0, {'product_id': product.id,
                                             'name': line_data.get('name').encode('utf-8'),
                                             'price_unit': line_data.get('price'),
                                             'product_uom_qty': line_data.get('quantity'),
                                             'product_uom': product.uom_id and product.uom_id.id,
                                             # 'tax_id': shopify_tax and [(6, 0, tax_ids)] or
                                             # [(6, 0, [])]
                                             }))
                else:
                    shopify_error_log += "\n" if shopify_error_log else ""
                    shopify_error_log += "Product does not exist"
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
                       }
            try:
                odoo_so_rec = so_env.create(so_vals)
            except:
                shopify_error_log += "\n" if shopify_error_log else ""
                shopify_error_log += "Order creation issue"
                pass

            # Now process picking
            # try:
            if not shopify_error_log and odoo_so_rec:
                odoo_so_id = odoo_so_rec.id
                odoo_so_name = odoo_so_rec.name or ''
                # product_moves_done = {}
                po_vals_list = []
                # Create internal transfers
                for fulfillment in fulfillments:
                    location_id = fulfillment.location_id
                    # print("location_id#######", location_id)
                    if location_id:
                        print("location_id---------",location_id)
                        s_location_id = self.env['shopify.locations'].sudo().search([('shopify_location_id', '=', str(location_id)), ('shopify_config_id', '=', shopify_config_id)], limit=1)
                        print("s_location_id***#####*****",s_location_id)
                        if s_location_id:
                            print("s_location_id********",s_location_id)
                            src_location_rec = self.env['stock.location'].sudo().search(
                                [('shopify_location_ids', '=', s_location_id.id)], limit=1)
                            if src_location_rec and shopify_location_id:
                                src_location_company_rec = src_location_rec.company_id
                                src_location_company = src_location_company_rec.id if src_location_company_rec else ''
                                shopify_location_company = shopify_location_rec.company_id.id if shopify_location_rec.company_id else ''
                                print("src_location_company**********",src_location_company)
                                print("shopify_location_company**********",shopify_location_company)
                                if src_location_company and shopify_location_company and shopify_location_company != src_location_company:
                                    multi_comp = True
                                else:
                                    multi_comp = False

                                if multi_comp:
                                    print("Process PO")
                                    vendor_picking_type_rec = self.env['stock.picking.type'].sudo().search(
                                        [('warehouse_id', '=', shopify_warehouse_id), ('code', '=', 'incoming')], limit=1)
                                    if vendor_picking_type_rec:
                                        po_lines_vals = []
                                        for line_item in fulfillment.line_items:
                                            line_data = line_item.attributes
                                            product = product_env.search(
                                                [('shopify_product_id', '=', line_data.get('variant_id'))]).product_variant_id
                                            if not product:
                                                product = product_variant_env.search(
                                                    [('default_code', '=', line_data.get('sku'))])

                                            if product:
                                                product_id = product.id
                                                product_name = product.name or ''
                                                qty_move = line_data.get('quantity')
                                                # if product_id in product_moves_done.keys():
                                                #     qty_update = product_moves_done[
                                                #         product_id] + qty_move
                                                #     product_moves_done.update(
                                                #         {product_id: qty_update})
                                                # else:
                                                #     product_moves_done.update(
                                                #         {product_id: qty_move})

                                                po_lines_vals.append((0, 0, {
                                                    'name': product_name,
                                                    'product_id': product_id,
                                                    'product_qty': qty_move,
                                                    'product_uom': product.uom_po_id.id,
                                                    'print_qty': qty_move,
                                                    'price_unit':0,
                                                    'date_planned': datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                                                    }))
                                            else:
                                                shopify_error_log += "\n" if shopify_error_log else ""
                                                shopify_error_log += "Product does not exist"
                                        print("po_lines_vals*****",po_lines_vals)
                                        po_vals = {'partner_id': shopify_vendor_id,
                                                   'company_id': company_id,
                                                   'origin': odoo_so_name,
                                                   'picking_type_id':vendor_picking_type_rec.id,
                                                   'order_line': po_lines_vals,
                                                   }
                                        process_po = True
                                        po_vals_list.append(po_vals)
                                        try:
                                            po_ids = po_env.sudo().search([('company_id','=', company_id),('partner_id','=', shopify_vendor_id), ('origin','=', odoo_so_name)], limit=1)
                                            print("search po_ids---",po_ids)
                                            if po_ids:
                                                po_ids.write({'order_line': po_lines_vals})
                                            else:
                                                odoo_po_rec = po_env.create(po_vals)
                                                print("search odoo_po_rec---",odoo_po_rec)
                                        except Exception as e:
                                            shopify_error_log += "\n" if shopify_error_log else ""
                                            shopify_error_log += "Purchase order creation issue - "+str(e)
                                            process_po = False
                                            pass
                                    print("po_vals_list*********",po_vals_list)
                                    # for po_vals_l in po_vals_list[0]:
                                    po_rec = po_env.sudo().search([('company_id','=', company_id),('partner_id','=', shopify_vendor_id), ('origin','=', odoo_so_name)], limit=1)
                                    print("po_ids*********",po_ids)
                                    if po_rec:
                                        po_rec.button_confirm()
                                        print("odoo_po_rec*********",po_rec)
                                        for picking in po_rec.picking_ids:
                                            for move in picking.move_lines:
                                                print("################",move.product_uom_qty)
                                                move.update({'quantity_done':move.product_uom_qty})
                                                # move.qty_done = move.product_uom_qty
                                                # for move_line in move.move_line_ids:
                                                #     move_line.quantity_done = move_line.product_uom_qty
                                                #     move_line.qty_done = move_line.product_uom_qty
                                            picking.action_done()

                                        src_shopify_customer_id = src_location_company_rec.shopify_customer_id.id
                                        src_shopify_warehouse_id = src_location_rec.m_warehouse_id.id

                                        src_so_vals = {'partner_id': src_shopify_customer_id,
                                               'company_id': src_location_company,
                                               'warehouse_id': src_shopify_warehouse_id,
                                               'order_line': po_lines_vals,
                                               'origin': odoo_so_name+' / '+ po_rec.name,
                                               'shopify_name':  str(shopify_order.order_number) or '',
                                               'shopify_order_id': str(shopify_order.id) or '',
                                               'shopify_note': shopify_order.note or '',
                                               'shopify_config_id': shopify_config_id,
                                               'shopify_fulfillment_status': fulfillment_status,
                                               'shopify_financial_status': financial_status,
                                               }
                                        print("src_so_vals****",src_so_vals)
                                        #Process Multi company Orders
                                        try:
                                            src_so_rec = so_env.create(src_so_vals)
                                        except:
                                            shopify_error_log += "\n" if shopify_error_log else ""
                                            shopify_error_log += "Order creation issue"
                                            pass

                                        shopify_error_log += self._process_so(src_so_rec)

                                else:
                                    self._process_internal_transfer(shopify_warehouse_id, src_location_rec, shopify_location_rec, odoo_so_name, fulfillment, company_id)
                                    ####Add following commented code in _process_internal_transfer function
                                    # picking_type_rec = self.env['stock.picking.type'].sudo().search(
                                    #     [('warehouse_id', '=', shopify_warehouse_id), ('code', '=', 'internal')], limit=1)
                                    # if picking_type_rec:
                                    #     move_lines_vals = []
                                    #     for line_item in fulfillment.line_items:
                                    #         line_data = line_item.attributes
                                    #         product = product_env.search(
                                    #             [('shopify_product_id', '=', line_data.get('variant_id'))]).product_variant_id
                                    #         if not product:
                                    #             product = product_variant_env.search(
                                    #                 [('default_code', '=', line_data.get('sku'))])

                                    #         if product:
                                    #             product_id = product.id
                                    #             qty_move = line_data.get('quantity')
                                    #             # if product_id in product_moves_done.keys():
                                    #             #     qty_update = product_moves_done[
                                    #             #         product_id] + qty_move
                                    #             #     product_moves_done.update(
                                    #             #         {product_id: qty_update})
                                    #             # else:
                                    #             #     product_moves_done.update(
                                    #             #         {product_id: qty_move})

                                    #             move_lines_vals.append((0, 0, {'product_id': product_id,
                                    #                                            'quantity_done': qty_move,
                                    #                                            'product_uom_qty': qty_move,
                                    #                                            'location_id': src_location_rec.id,
                                    #                                            'location_dest_id': shopify_location_id,
                                    #                                            'product_uom': product.uom_id.id,
                                    #                                            'name': src_location_rec.name}))
                                    #         else:
                                    #             shopify_error_log += "\n" if shopify_error_log else ""
                                    #             shopify_error_log += "Product does not exist"
                                    #     sp_vals = {'location_id': src_location_rec.id,
                                    #                'location_dest_id': shopify_location_id,
                                    #                'picking_type_id': picking_type_rec.id,
                                    #                'move_lines': move_lines_vals,
                                    #                'company_id': company_id,
                                    #                'origin': odoo_so_name,
                                    #                }
                                    #     sp_id = self.env['stock.picking'].create(sp_vals)
                                    #     sp_id.button_validate()
                shopify_error_log += self._process_so(odoo_so_rec)
                ####Add following commente code in _process_so function
                # try:
                #     process_order = True
                #     odoo_so_rec.action_confirm()
                # except:
                #     shopify_error_log += "\n" if shopify_error_log else ""
                #     shopify_error_log += "Order confirmation issue"
                #     process_order = False
                #     pass

                # if process_order:
                #     try:
                #         pick_to_backorder = self.env['stock.picking']
                #         pick_to_do = self.env['stock.picking']
                #         so_picking_ids = odoo_so_rec.picking_ids
                #         for picking in so_picking_ids:
                #             for move in picking.move_lines:
                #                 for move_line in move.move_line_ids:
                #                     if move_line.product_id.id in product_moves_done.keys():
                #                         move_line.quantity_done = product_moves_done[
                #                             move_line.product_id.id]
                #                         move_line.qty_done = product_moves_done[
                #                             move_line.product_id.id]
                #                     else:
                #                         move_line.quantity_done = 0
                #                         move_line.qty_done = 0
                #             # Done picking with no backorder
                #             picking.action_done()
                #             backorder_pick = self.env['stock.picking'].search(
                #                 [('backorder_id', '=', picking.id)])
                #             backorder_pick.action_cancel()

                #         picking_not_process = so_picking_ids.filtered(lambda picking_id: picking_id.state in ['done','cancel'])
                #         print("picking_not_process*************",picking_not_process)
                #         if not picking_not_process:
                #             process_order = False
                #             shopify_error_log += "\n" if shopify_error_log else ""
                #             shopify_error_log += "Order DO processing issue"
                #     except:
                #         shopify_error_log += "\n" if shopify_error_log else ""
                #         shopify_error_log += "Order DO processing issue"
                #         process_order = False
                #         pass
                #     if not odoo_so_rec.invoice_ids and process_order:
                #         try:
                #             odoo_so_invoice = odoo_so_rec.action_invoice_create()
                #             invoice = self.env['account.invoice'].browse(
                #                 odoo_so_invoice[0])
                #             invoice.action_invoice_open()
                #         except:
                #             shopify_error_log += "\n" if shopify_error_log else ""
                #             shopify_error_log += "Order invoice creation and validation issue"
                #             pass

        if shopify_error_log:
            self.env['shopify.order.error.log'].create({
                'error': shopify_error_log,
                'shopify_config_id': shopify_config_id,
                'company_id': company_id,
                'date': fields.Date.today(),
                'shopify_so_id': str(shopify_order.id) or '',
                'odoo_so_id': odoo_so_id,
            })


    def _process_internal_transfer(self, warehouse_id, location_id, location_dest_id, odoo_so_name, fulfillment, company_id):
        picking_type_rec = self.env['stock.picking.type'].sudo().search(
                                        [('warehouse_id', '=', warehouse_id),
                                        ('code', '=', 'internal')], limit=1)
        shopify_error_log = ""
        product_env = self.env['shopify.product.product']
        product_variant_env = self.env['product.product']
        if picking_type_rec:
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
                    # if product_id in product_moves_done.keys():
                    #     qty_update = product_moves_done[
                    #         product_id] + qty_move
                    #     product_moves_done.update(
                    #         {product_id: qty_update})
                    # else:
                    #     product_moves_done.update(
                    #         {product_id: qty_move})

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
            sp_id = self.env['stock.picking'].create(sp_vals)
            sp_id.button_validate()
        else:
            shopify_error_log += "\n" if shopify_error_log else ""
            shopify_error_log += "Picking type not found for warehouse id - "+str(warehouse_id)
        return shopify_error_log