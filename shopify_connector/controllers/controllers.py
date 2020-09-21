# -*- coding: utf-8 -*-

import logging

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)
_order_list = []


class ShopifyOdooConnector(http.Controller):

    @http.route('/shopify/<string:config_name>/order', type='json', auth="none", methods=['POST'], csrf=False)
    def shopify_order(self, config_name):
        """
        1. Check order id in order cache i.e. _order_list
        2. If order_id exists in order cache then return a function else check for order's financial status and fulfillment status
        3. Only allow importing those orders whose orders status is financial_status is 'paid' and fulfillment_status is 'fulfilled' Or financial_status is 'partially_refunded' and fulfillment_status is 'partial'
        4. If an order is importable then check with the Shopify configuration
        5. If Shopify configuration exists then test the connection to makes sure that all API configuration correct
        6. Using Shopify configuration and order_id fetch company_id for sale order
        7. Base on the company gets salesperson from the company
        8. Using the salesperson execute an import_order function of Shopify config
        """
        _logger.info("*******Webhook call for %s config*******", config_name)
        if request.jsonrequest:
            shopify_order_id = request.jsonrequest.get('id')
            if shopify_order_id in _order_list:
                _logger.info("#Webhook Call End for %s config*******", config_name)
                return True
            else:
                _order_list.append(shopify_order_id)
            try:
                shopify_financial_status = request.jsonrequest.get(
                    'financial_status')
                shopify_fulfillment_status = request.jsonrequest.get(
                    'fulfillment_status')
                if config_name and shopify_order_id:
                    allow_import = False
                    if shopify_financial_status == 'paid' and shopify_fulfillment_status == 'fulfilled':
                        allow_import = True
                    elif shopify_financial_status == 'partially_refunded' and shopify_fulfillment_status == 'partial':
                        allow_import = True
                    if allow_import:
                        shopify_config_rec = request.env['shopify.config'].sudo().search([('name', '=', config_name)], limit=1)
                        if shopify_config_rec:
                            shopify_config_rec.test_connection()
                            order_company = shopify_config_rec.get_shopify_order_company(shopify_order_id)
                            shopify_config_rec.sudo(order_company.shopify_user_id.id).import_order(
                                shopify_order_id, order_company, allow_import)
                        else:
                            _logger.error("%s config record not found*******", config_name)
            except:
                pass
            if shopify_order_id in _order_list:
                _order_list.remove(shopify_order_id)
        _logger.info("*******Webhook Call End for %s config*******", config_name)
        return True
