# coding: utf-8

import logging

from odoo import api, fields, models, tools, _
from odoo.addons import decimal_precision as dp
# from odoo.exceptions import UserError, ValidationError
# from datetime import datetime

_logger = logging.getLogger(__name__)

class ProductTemplate(models.Model):
    _inherit='product.template'

    bck_stock_date = fields.Datetime('Back In Stock Date', company_dependent=True)

