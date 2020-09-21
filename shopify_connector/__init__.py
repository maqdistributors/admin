# -*- coding: utf-8 -*-

import logging

from . import models
from . import controllers
from . import wizard

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


# TODO: Apply proper fix & remove in master
def _create_company_records(cr, registry):
    """
    Create and set following feilds in the company master while installing module
    shopify_vendor_id, shopify_customer_id, shopify_warehouse_id, and shopify_location_id
    """
    env = api.Environment(cr, SUPERUSER_ID, {})

    partner_env = env['res.partner']
    pricelist_env = env['product.pricelist']
    warehouse_env = env['stock.warehouse']

    for company in env['res.company'].search([]):
        company_vals = {}
        company_name = str(company.name) or ''
        code = "SW"

        for letter in company_name.split():
            code += letter[0]
            if len(code) == 5:
                break
        try:
            shopify_vendor_id = partner_env.create(
                {'name': 'Shopify Vendor - ' + company_name, 'supplier': True, 'customer': False, 'company_id': company.id})
            company_vals.update({'shopify_vendor_id': shopify_vendor_id.id})
        except Exception as e:
            _logger.error(
                'Vendor is not created in the system for the company - ' + company_name + ' : %s', e)
            pass

        try:
            pricelist_rec = pricelist_env.create(
                {'name': 'Shopify pricelist -' + company_name, 'discount_policy': 'with_discount',
                 'company_id': company.id})
        except Exception as e:
            _logger.error(
                'Pricelist is not created in the system for the company - ' + company_name + ' : %s', e)
            pass

        if pricelist_rec:
            cust_vals = {'name': 'Shopify Customer - ' + company_name,
                         'property_product_priclist': pricelist_rec.id,
                         'supplier': False, 'customer': True,
                         'company_id': company.id}
        else:
            cust_vals = {'name': 'Shopify Customer - ' + company_name,
                         'supplier': False, 'customer': True,
                         'company_id': company.id}
        try:
            shopify_customer_id = partner_env.create(cust_vals)
            company_vals.update(
                {'shopify_customer_id': shopify_customer_id.id})
        except Exception as e:
            _logger.error(
                'Customer is not created in the system for the company - ' + company_name + ' : %s', e)
            pass

        warehouse_code_search = warehouse_env.search_count(
            [('code', '=', code)])
        if warehouse_code_search > 0:
            count = 1
            while warehouse_code_search > 0:
                code = code[:-1] + \
                    str(count) if len(code) >= 5 else code + str(count)
                count = count + 1
                warehouse_code_search = warehouse_env.search_count(
                    [('code', '=', code)])

        try:
            shopify_warehouse_id = warehouse_env.create(
                {'name': 'Shopify Warehouse - ' + company_name + '[' + code + ']', 'code': code,
                 'company_id': company.id})
            shopify_location_id = shopify_warehouse_id.lot_stock_id
            company_vals.update({'shopify_warehouse_id': shopify_warehouse_id.id,
                                 'shopify_location_id': shopify_location_id.id})
        except Exception as e:
            _logger.error(
                'Warehouse is not created in the system for the company - ' + company_name + ' : %s', e)
            pass

        if company_vals:
            try:
                company.write(company_vals)
            except:
                _logger.error(
                    'Company data is not created in the system for the company - ' + company_name + ' : %s', e)
                pass
