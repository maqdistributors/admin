# coding: utf-8

import logging

from odoo import api, fields, models, tools
from odoo.http import request
from odoo.osv import expression

_logger = logging.getLogger(__name__)


class Website(models.Model):
    _inherit = 'website'

    website_auto_pricelist = fields.Boolean('Website Auto Pricelist')
    # default_pricelist = fields.Many2one('product.pricelist', 'Default Pricelist', domain="[('company_id', '=', company_id)]")