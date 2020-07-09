# -*- coding: utf-8 -*-
# Part of Bistasolutions. See LICENSE file for full copyright and licensing details.
import logging
from datetime import timedelta
from functools import partial

import psycopg2
import pytz

from odoo import api, fields, models, tools, _
from odoo.tools import float_is_zero
from odoo.exceptions import UserError
from odoo.http import request
from odoo.addons import decimal_precision as dp

_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = "res.users"
    product_categ_ids = fields.Many2many('product.category', string='Restrict Internal Product Categories',
                                                 help='The sale order will not display products which are within one of the selected category trees. If no category is specified, all available sale order will be shown')

    @api.multi
    def write(self, vals):
        res = super(ResUsers, self).write(vals)
        myrule = self.env.ref('maq_point_of_sale.filter_user_product_category_allowed')
        if myrule:
            myrule.domain_force = myrule.domain_force
        return res
