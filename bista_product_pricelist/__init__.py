# -*- coding: utf-8 -*-

import logging

from . import models

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)

def _update_sales_pricelist(cr, registry):

    env = api.Environment(cr, SUPERUSER_ID, {})

    products = env['product.template'].search([])

    for product in products:
        product_vals = {}
        product_name = str(product.name) or ''

        ppis = product.item_ids

        sales_pricelist = False
        if ppis:
            for ppi in ppis:
                if ppi.min_quantity in [0,1] and ppi.date_start == False and ppi.date_end == False:

                    sales_pricelist = ppi.fixed_price
                    print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>',sales_pricelist)

            product_vals.update({'sales_pricelist':sales_pricelist})

        if product_vals:
            try:
                product.write(product_vals)
            except Exception as e:
                _logger.error(
                    'product name - ' + product_name + ' : %s', e)
                pass
