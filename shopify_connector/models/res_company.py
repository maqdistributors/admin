# -*- coding: utf-8 -*-

from odoo import models, fields


class ResCompany(models.Model):
    _inherit = "res.company"

    shopify_vendor_id = fields.Many2one(
        "res.partner", "Shopify Vendor", help="Shopify Vendor", track_visibility="onchange")
    shopify_customer_id = fields.Many2one(
        "res.partner", "Shopify Customer", help="Shopify Customer", track_visibility="onchange")
    shopify_warehouse_id = fields.Many2one(
        "stock.warehouse", "Shopify Warehouse",  help="Shopify Warehouse", track_visibility="onchange")
    shopify_province_ids = fields.Many2many("res.country.state", 'res_company_state_rel', 'res_company_id',
                                            'res_state_id', "Shopify Province",  help="Shopify Province", track_visibility="onchange")
    shopify_location_id = fields.Many2one("stock.location", "Shopify Stock Location",
                                          help="Here you can set default Shopify Stock Location", track_visibility="onchange")
    shopify_user_id = fields.Many2one("res.users", "Default User", track_visibility="onchange", required=True,
                                      help="Default user who'll create SO and PO for a company")
    shopify_intercompany_customer_id = fields.Many2one(
        "res.partner", "Shopify Intercompany Customer", help="Shopify Intercompany Customer", track_visibility="onchange")
