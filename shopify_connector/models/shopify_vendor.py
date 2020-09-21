# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ShopifyVendor(models.Model):
    _name = 'shopify.vendor'
    _description = 'Shopify Vendor'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']

    name = fields.Char("Name", help="Enter Name",
                       required=True, track_visibility="onchange")
    shopify_config_id = fields.Many2one("shopify.config", required=True, string="Shopify Configuration",
                                        help="Enter Shopify Configuration", track_visibility='onchange')
