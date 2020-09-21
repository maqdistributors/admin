# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ShopifyOrderErrorLog(models.Model):
    _name = 'shopify.order.error.log'
    _description = 'Shopify Order Error Log'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _order = "create_date desc"

    shopify_so_id = fields.Char(
        "Shopify SO ID", help="Enter Shopify SO ID", track_visibility="onchange")
    odoo_so_id = fields.Many2one("sale.order", "Odoo Sale Order ID",
                                 help="Enter Sale Order ID", track_visibility="onchange")
    error = fields.Text("Error", help="Error Message",
                        track_visibility="onchange")
    company_id = fields.Many2one(
        "res.company", "Company", help="Company", track_visibility="onchange")
    date = fields.Date("Date", help="Company", track_visibility="onchange")
    shopify_config_id = fields.Many2one(
        "shopify.config", "Shopify Config.", help="Shopify Config.", track_visibility="onchange")
