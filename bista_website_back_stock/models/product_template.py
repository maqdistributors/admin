# coding: utf-8

import logging

from odoo import api, fields, models, tools, _
_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    bck_stock_date = fields.Datetime('Back In Stock Date', company_dependent=True)
