# -*- coding: utf-8 -*-
# Part of Bistasolutions. See LICENSE file for full copyright and licensing details.
import logging
from datetime import timedelta
from functools import partial

import psycopg2
import pytz

from odoo import api, fields, models, tools, _
from odoo.osv import expression
from odoo.tools import float_is_zero
from odoo.exceptions import UserError
from odoo.http import request
from odoo.addons import decimal_precision as dp

_logger = logging.getLogger(__name__)


class ProductProduct(models.Model):
    _inherit = "product.product"

    # @api.model
    # def name_search(self, name='', args=None, operator='ilike', limit=100):
    #     # TDE FIXME: currently overriding the domain; however as it includes a
    #     # search on a m2o and one on a m2m, probably this will quickly become
    #     # difficult to compute - check if performance optimization is required
    #     if name and operator in ('=', 'ilike', '=ilike', 'like', '=like'):
    #         args = args or []
    #         product_categ_ids = self.env.user.product_categ_ids.ids
    #         if product_categ_ids:
    #             domain = [('categ_id', 'not in', product_categ_ids)]
    #             print("-------------------domain",domain)
    #             return self.search(expression.AND([domain, args]), limit=limit).name_get()
    #     return super(ProductProduct, self).name_search(name=name, args=args, operator=operator, limit=limit)
