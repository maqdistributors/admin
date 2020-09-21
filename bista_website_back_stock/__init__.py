# -*- coding: utf-8 -*-
import logging

from . import controllers
from . import models

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def _update_back_in_stock(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    ir_property = env['ir.property']
    product = env['product.product']
    ir_domain = [('name', '=', 'is_website_publish'), ('value_integer', '=', 1)]
    ir_property_ids = ir_property.search(ir_domain)
    product_list = []
    if ir_property_ids:
        for ir_property_id in ir_property_ids:
            res_id = ir_property_id.res_id
            res_val = res_id.split(',')
            product_id = int(res_val[1])
            product_list.append(product_id)
    if product_list:
        products = product.search([('id', 'not in', product_list), ('sale_ok', '=', True)])
    if products:
        for product in products:
            product_template = product.product_tmpl_id
            if product_template:
                try:
                    product_template.update({'bck_stock_date': product.__last_update})
                except Exception as e:
                    _logger.error(
                        'product back in stock date update - ' + product_template.name + ' : %s', e)
                    pass
            print("product_template>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>", product_template)
