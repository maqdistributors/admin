# -*- coding: utf-8 -*-
# Part of Bista. See LICENSE file for full copyright and licensing details.

from odoo import http, fields
from odoo.http import request
from odoo.addons.sale.controllers.product_configurator import ProductConfiguratorController


class WebsiteSale(ProductConfiguratorController):

    def _show_optional_products(self, product_id, variant_values, pricelist, handle_stock, **kw):
        product = request.env['product.product'].with_context(self._get_product_context(pricelist, **kw)).browse(
            int(product_id))
        combination = request.env['product.template.attribute.value'].browse(variant_values)
        has_optional_products = product.optional_product_ids.filtered(lambda p: p._is_add_to_cart_possible(combination))

        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>product_id", product_id)

        # if not has_optional_products:
        #     return False

        add_qty = int(kw.get('add_qty', 1))
        to_currency = (pricelist or product).currency_id
        company = request.env['res.company'].browse(request.env.context.get('company_id')) or request.env[
            'res.users']._get_company()
        date = request.env.context.get('date') or fields.Date.today()

        def compute_currency(price):
            return product.currency_id._convert(price, pricelist.currency_id,
                                                product._get_current_company(pricelist=pricelist,
                                                                             website=request.website),
                                                fields.Date.today())

        no_variant_attribute_values = combination.filtered(
            lambda
                product_template_attribute_value: product_template_attribute_value.attribute_id.create_variant == 'no_variant'
        )
        if no_variant_attribute_values:
            product = product.with_context(no_variant_attribute_values=no_variant_attribute_values)

        return request.env['ir.ui.view'].render_template("sale.optional_products_modal", {
            'product': product,
            'combination': combination,
            'add_qty': add_qty,
            # reference_product deprecated, use combination instead
            'reference_product': product,
            'variant_values': variant_values,
            'pricelist': pricelist,
            # compute_currency deprecated, get from pricelist or product
            'compute_currency': compute_currency,
            # to_currency deprecated, get from pricelist or product
            'to_currency': to_currency,
            'handle_stock': handle_stock,
            # get_attribute_exclusions deprecated, use product method
            'get_attribute_exclusions': self._get_attribute_exclusions,
        })
