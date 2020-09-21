# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ShopifyProdTags(models.Model):
    _name = 'shopify.prod.tags'
    _description = 'Shopify Product Tags'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']

    name = fields.Char('Name', help='Enter Name',
                       track_visibility='onchange', required=True)
    shopify_config_ids = fields.Many2many('shopify.config', string='Shopify Configurations',
                                          help='Enter Shopify Configurations', track_visibility='onchange', required=True)
    color = fields.Integer('Color', help='Enter the Color',
                           track_visibility='onchange')
    is_province = fields.Boolean(
        'Province', help='Province Yes/No', track_visibility='onchange')
    active = fields.Boolean('Active', help='Active Yes/No',
                            track_visibility='onchange', default=True)
