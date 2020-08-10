# -*- coding: utf-8 -*-
# Part of Bistasolutions. See LICENSE file for full copyright and licensing details.
import logging
from odoo import api, fields, models, tools, _
from odoo.addons import decimal_precision as dp

_logger = logging.getLogger(__name__)


class ProductProduct(models.Model):
    _inherit = "product.product"
    product_format = fields.Float(string="Product Format", digits=dp.get_precision('Weight Precision Three'))
    reporting_weight = fields.Float(string="Reporting Weight", digits=dp.get_precision('Weight Precision Three'))
    equivalent_weight = fields.Float(string="Cannabis Equivalent Weight",
                                     digits=dp.get_precision('Weight Precision Three'))
    product_format_uom_id = fields.Many2one('product.uom', 'Product Format Unit of Measure')
