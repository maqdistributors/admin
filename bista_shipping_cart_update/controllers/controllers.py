# -*- coding: utf-8 -*-
import logging

from odoo import http, tools, _
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
from datetime import datetime

_logger = logging.getLogger(__name__)


class WebsiteSale(WebsiteSale):

    def recalculate_prices(self, order):
        now = datetime.now()
        for line in order.mapped('order_line'):
            dict = line._convert_to_write(line.read()[0])
            if 'product_tmpl_id' in line._fields:
                dict['product_tmpl_id'] = line.product_tmpl_id
            line2 = request.env['sale.order.line'].new(dict)
            # we make this to isolate changed values:
            line2.sudo().product_uom_change()
            line2.sudo()._onchange_discount()
            line.write({
                'price_unit': line2.price_unit,
                'discount': line2.discount,
            })
        order.write({
            'date_order': now,
        })
        return True

    @http.route(['/shop/cart'], type='http', auth="public", website=True)
    def cart(self, access_token=None, revive='', **post):
        """
        Main cart management + abandoned cart revival
        access_token: Abandoned cart SO access token
        revive: Revival method when abandoned cart. Can be 'merge' or 'squash'
        """
        order = request.website.sale_get_order()
        if order and order.state != 'draft':
            request.session['sale_order_id'] = None
            order = request.website.sale_get_order()
        values = {}
        if access_token:
            abandoned_order = request.env['sale.order'].sudo().search([('access_token', '=', access_token)], limit=1)
            if not abandoned_order:  # wrong token (or SO has been deleted)
                return request.render('website.404')
            if abandoned_order.state != 'draft':  # abandoned cart already finished
                values.update({'abandoned_proceed': True})
            elif revive == 'squash' or (revive == 'merge' and not request.session[
                'sale_order_id']):  # restore old cart or merge with unexistant
                request.session['sale_order_id'] = abandoned_order.id
                return request.redirect('/shop/cart')
            elif revive == 'merge':
                abandoned_order.order_line.write({'order_id': request.session['sale_order_id']})
                abandoned_order.action_cancel()
            elif abandoned_order.id != request.session[
                'sale_order_id']:  # abandoned cart found, user have to choose what to do
                values.update({'access_token': abandoned_order.access_token})
        self.recalculate_prices(order)
        if order:
            from_currency = order.company_id.currency_id
            to_currency = order.pricelist_id.currency_id
            compute_currency = lambda price: from_currency.compute(price, to_currency)
        else:
            compute_currency = lambda price: price
        values.update({
            'website_sale_order': order,
            'compute_currency': compute_currency,
            'suggested_products': [],
        })
        if order:
            _order = order
            if not request.env.context.get('pricelist'):
                _order = order.with_context(pricelist=order.pricelist_id.id)
            values['suggested_products'] = _order._cart_accessories()
        if post.get('type') == 'popover':
            # force no-cache so IE11 doesn't cache this XHR
            return request.render("website_sale.cart_popover", values, headers={'Cache-Control': 'no-cache'})
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>shipping cart", values)
        return request.render("website_sale.cart", values)
