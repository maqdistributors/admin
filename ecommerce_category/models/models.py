# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ProductPublicCategory(models.Model):
    _inherit='product.public.category'

    website_id = fields.Many2one('website', string='Website')
    parent_website_id = fields.Many2one(related='parent_id.website_id', string='Website')