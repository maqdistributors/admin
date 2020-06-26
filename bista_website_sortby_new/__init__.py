# -*- coding: utf-8 -*-

import logging

from . import models

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)

def _update_publish_date(cr, registry):

    env = api.Environment(cr, SUPERUSER_ID, {})

    products = env['product.template'].search([('sale_ok','=', True)])

    for product in products:
        product_vals = {}
        product_name = str(product.name) or ''
        product_vals.update({'publish_date':product.create_date})

        if product_vals:
            try:
                product.write(product_vals)
            except Exception as e:
                _logger.error(
                    'product name - ' + product_name + ' : %s', e)
                pass
