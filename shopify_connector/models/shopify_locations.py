# -*- coding: utf-8 -*-

import logging
from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class ShopifyLocations(models.Model):
    _name = 'shopify.locations'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = 'Shopify Locations'

    shopify_config_id = fields.Many2one("shopify.config", "Shopify Configuration",
                                        help="Enter Shopify Config.", track_visibility='onchange', required=True)
    shopify_location_id = fields.Char(
        string="Shopify Location ID", help="Enter Shopify Location ID", track_visibility='onchange', required=True)
    name = fields.Char("Name", help="Enter Name",
                       track_visibility='onchange', required=True)
    address1 = fields.Char(
        "Address1", help="Enter Address1", track_visibility='onchange')
    address2 = fields.Char(
        "Address2", help="Enter Address2", track_visibility='onchange')
    city = fields.Char("City", help="Enter City", track_visibility='onchange')
    zip = fields.Char("Zip", help="Enter Zip", track_visibility='onchange')
    province = fields.Char(
        "Province", help="Enter Province", track_visibility='onchange')
    # country = fields.Char("Country", help="Enter Country", track_visibility='onchange')
    phone = fields.Char("Phone", help="Enter Phone",
                        track_visibility='onchange')
    created_at_shopify = fields.Char(
        "Created at Shopify", help="Enter Created at Shopify", track_visibility='onchange')
    updated_at_shopify = fields.Char(
        "Updated at Shopify", help="Enter Updated at Shopify", track_visibility='onchange')
    country_code = fields.Char(
        "Country Code", help="Enter Country Code", track_visibility='onchange')
    country_name = fields.Char(
        "Country Name", help="Enter Country Name", track_visibility='onchange')
    province_code = fields.Char(
        "Province Code", help="Enter Province Code", track_visibility='onchange')
    legacy = fields.Char("Legacy", help="Enter Legacy",
                         track_visibility='onchange')
    active = fields.Boolean("Active", help="Enter Active",
                            track_visibility='onchange', default=True)

    @api.multi
    def check_shopify_location_id_uniq(self):
        for rec in self:
            search_product_count = self.sudo().search_count(
                [('shopify_location_id', '=', rec.shopify_location_id)])
            if search_product_count > 1:
                return False
            else:
                return True

    _constraints = [
        (check_shopify_location_id_uniq,
         'Shopify location id must be unique!', ['shopify_location_id']),
    ]


class StockLocation(models.Model):
    _inherit = 'stock.location'

    shopify_location_ids = fields.Many2many(
        'shopify.locations', help="Enter Shopify Locations")

    @api.multi
    def shopify_location_id_select(self):
        for rec in self:
            location_count = len(rec.shopify_location_ids)
            if location_count > 1:
                return False
            else:
                return True

    _constraints = [
        (shopify_location_id_select,
         'You can select only one shopify location!', ['shopify_location_ids']),
    ]

class StockPicking(models.Model):

    _inherit = 'stock.picking'

    shopify_fulfillment_id = fields.Char(
        "Shopify Fulfillment ID", help='Enter Shopify Fullfillment ID', readonly=True)
    shopify_order_id = fields.Char(
        "Shopify Order ID", help='Enter Shopify Order ID', readonly=True)

class StockMove(models.Model):

    _inherit = 'stock.move'

    def _check_location_config(self, location_id, location_dest_id):
        """
        Warning raise if account are wrongly configured in locations
        'Cannot create moves for different companies.'
        till that time shopify call is executed. To avoid this
        function will try to access configure accounts and it's company
        """
        if location_id:
            valuation_in_account_id = location_id.valuation_in_account_id
            if valuation_in_account_id:
                location_company_id = valuation_in_account_id.company_id
        if location_dest_id:
            valuation_out_account_id = location_dest_id.valuation_out_account_id
            if valuation_out_account_id:
                location_dest_company_id = valuation_out_account_id.company_id

    def _action_done(self):
        moves = super(StockMove, self)._action_done()
        move_ids = moves.filtered(lambda mv:mv.state == 'done')
        for move in move_ids:
            shopify_picking = self._context.get('shopify_picking_validate')
            if not shopify_picking:
                try:
                    shopify_prod_obj = self.env['shopify.product.product']
                    shopify_export_val = False
                    for move_line in move.move_line_ids:
                        product_rec = move_line.product_id
                        product_id = product_rec.id
                        product_count = shopify_prod_obj.sudo().search_count(
                            [('product_variant_id', '=', product_id), ('shopify_product_id', 'not in', ('', False))])
                        if product_count > 0:
                            qty = move_line.qty_done
                            if qty > 0:
                                negative_qty = qty * -1
                                location_id = move_line.location_id
                                location_dest_id = move_line.location_dest_id
                                self._check_location_config(location_id,location_dest_id)
                                if location_id:
                                    for shopify_location_rec in location_id.shopify_location_ids:
                                        shopify_config_rec = shopify_location_rec.shopify_config_id
                                        shopify_location_id = shopify_location_rec.shopify_location_id
                                        inventory_item_id = shopify_prod_obj.sudo().search([('product_variant_id', '=', product_id), (
                                            'shopify_config_id', '=', shopify_config_rec.id)], limit=1).shopify_inventory_item_id
                                        shopify_product_cost = product_rec.standard_price
                                        product_inventory_valuation = product_rec.categ_id.property_valuation
                                        if inventory_item_id and product_inventory_valuation == 'manual_periodic':
                                            shopify_config_rec.sudo().update_shopify_inventory(
                                                shopify_location_id, inventory_item_id, int(negative_qty))
                                            shopify_export_val = True
                                        elif inventory_item_id and product_inventory_valuation == 'real_time' and shopify_product_cost > 0:
                                            shopify_config_rec.sudo().update_shopify_inventory(
                                                shopify_location_id, inventory_item_id, int(negative_qty))
                                            shopify_export_val = True
                                if location_dest_id:
                                    for shopify_location_rec in location_dest_id.shopify_location_ids:
                                        shopify_config_rec = shopify_location_rec.shopify_config_id
                                        shopify_location_id = shopify_location_rec.shopify_location_id
                                        inventory_item_id = shopify_prod_obj.sudo().search([('product_variant_id', '=', product_id), (
                                            'shopify_config_id', '=', shopify_config_rec.id)], limit=1).shopify_inventory_item_id
                                        shopify_product_cost = product_rec.standard_price
                                        product_inventory_valuation = product_rec.categ_id.property_valuation
                                        if inventory_item_id and product_inventory_valuation == 'manual_periodic':
                                            shopify_config_rec.sudo().update_shopify_inventory(
                                                shopify_location_id, inventory_item_id, int(qty))
                                            shopify_export_val = True
                                        elif inventory_item_id and product_inventory_valuation == 'real_time' and shopify_product_cost > 0:
                                            shopify_config_rec.sudo().update_shopify_inventory(
                                                shopify_location_id, inventory_item_id, int(qty))
                                            shopify_export_val = True
                        if shopify_export_val:
                            move_line.shopify_export = shopify_export_val
                except Exception as e:
                    _logger.error('Stock update operation have following error: %s', e)
                    move.shopify_error_log = str(e)
                    pass
        return moves

class StockMoveLine(models.Model):

    _inherit = 'stock.move.line'

    shopify_error_log = fields.Text(
        "Shopify Error", help="Error occurs while exporting move to the shopify",
        readonly=True)
    shopify_export = fields.Boolean(
        "Shopify Export", help="Enter Shopify Export", readonly=True)

    # def _check_location_config(self, location_id, location_dest_id):
    #     """
    #     Warning raise if account are wrongly configured in locations
    #     'Cannot create moves for different companies.'
    #     till that time shopify call is executed. To avoid this
    #     function will try to access configure accounts and it's company
    #     """
    #     if location_id:
    #         valuation_in_account_id = location_id.valuation_in_account_id
    #         if valuation_in_account_id:
    #             location_company_id = valuation_in_account_id.company_id
    #     if location_dest_id:
    #         valuation_out_account_id = location_dest_id.valuation_out_account_id
    #         if valuation_out_account_id:
    #             location_dest_company_id = valuation_out_account_id.company_id

    # def _action_done(self):
    #     res = super(StockMoveLine, self)._action_done()
    #     # exclude the method call if action done happening while shopify order import
    #     shopify_picking = self._context.get('shopify_picking_validate')
    #     if not shopify_picking:
    #         try:
    #             shopify_prod_obj = self.env['shopify.product.product']
    #             shopify_export_val = False
    #             for move in self:
    #                 product_rec = move.product_id
    #                 product_id = product_rec.id
    #                 product_count = shopify_prod_obj.sudo().search_count(
    #                     [('product_variant_id', '=', product_id), ('shopify_product_id', 'not in', ('', False))])
    #                 if product_count > 0:
    #                     qty = move.qty_done
    #                     if qty > 0:
    #                         negative_qty = qty * -1
    #                         location_id = move.location_id
    #                         location_dest_id = move.location_dest_id
    #                         self._check_location_config(location_id,location_dest_id)
    #                         if location_id:
    #                             for shopify_location_rec in location_id.shopify_location_ids:
    #                                 shopify_config_rec = shopify_location_rec.shopify_config_id
    #                                 shopify_location_id = shopify_location_rec.shopify_location_id
    #                                 inventory_item_id = shopify_prod_obj.sudo().search([('product_variant_id', '=', product_id), (
    #                                     'shopify_config_id', '=', shopify_config_rec.id)], limit=1).shopify_inventory_item_id
    #                                 shopify_product_cost = product_rec.standard_price
    #                                 product_inventory_valuation = product_rec.categ_id.property_valuation
    #                                 if inventory_item_id and product_inventory_valuation == 'manual_periodic':
    #                                     shopify_config_rec.sudo().update_shopify_inventory(
    #                                         shopify_location_id, inventory_item_id, int(negative_qty))
    #                                     shopify_export_val = True
    #                                 elif inventory_item_id and product_inventory_valuation == 'real_time' and shopify_product_cost > 0:
    #                                     shopify_config_rec.sudo().update_shopify_inventory(
    #                                         shopify_location_id, inventory_item_id, int(negative_qty))
    #                                     shopify_export_val = True
    #                         if location_dest_id:
    #                             for shopify_location_rec in location_dest_id.shopify_location_ids:
    #                                 shopify_config_rec = shopify_location_rec.shopify_config_id
    #                                 shopify_location_id = shopify_location_rec.shopify_location_id
    #                                 inventory_item_id = shopify_prod_obj.sudo().search([('product_variant_id', '=', product_id), (
    #                                     'shopify_config_id', '=', shopify_config_rec.id)], limit=1).shopify_inventory_item_id
    #                                 shopify_product_cost = product_rec.standard_price
    #                                 product_inventory_valuation = product_rec.categ_id.property_valuation
    #                                 if inventory_item_id and product_inventory_valuation == 'manual_periodic':
    #                                     shopify_config_rec.sudo().update_shopify_inventory(
    #                                         shopify_location_id, inventory_item_id, int(qty))
    #                                     shopify_export_val = True
    #                                 elif inventory_item_id and product_inventory_valuation == 'real_time' and shopify_product_cost > 0:
    #                                     shopify_config_rec.sudo().update_shopify_inventory(
    #                                         shopify_location_id, inventory_item_id, int(qty))
    #                                     shopify_export_val = True
    #                 if shopify_export_val:
    #                     move.shopify_export = shopify_export_val
    #         except Exception as e:
    #             _logger.error('Stock update operation have following error: %s', e)
    #             move.shopify_error_log = str(e)
    #             pass
    #     return res
