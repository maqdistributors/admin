# coding: utf-8

import logging

from odoo import api, fields, models, tools
from odoo.http import request
from odoo.osv import expression

_logger = logging.getLogger(__name__)


class Website(models.Model):
    _inherit = 'website'

    website_shop_login = fields.Boolean(string='Requires registration to shop')
    website_shop_login_redirect = fields.Char(string='Registration URL')
    search_all_products = fields.Boolean("Search All Products", help="Search all products regardless of the category on which currently you are.")
