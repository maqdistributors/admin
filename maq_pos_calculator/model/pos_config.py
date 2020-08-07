# -*- coding: utf-8 -*-
# Part of Bistasolutions. See LICENSE file for full copyright and licensing details.
import logging
from odoo import api, fields, models, tools, _
from odoo.addons import decimal_precision as dp

_logger = logging.getLogger(__name__)


class PosConfig(models.Model):
    _inherit = "pos.config"
    cannabis_purchase_limit = fields.Float(string="Cannabis Purchase Limit", digits=dp.get_precision('Weight Precision Three'))
