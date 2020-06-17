# coding: utf-8

import logging

from odoo import api, fields, models, tools, _
from odoo.tools import pycompat
from odoo.tools import float_compare
# from odoo.addons import decimal_precision as dp
# from odoo.exceptions import UserError, ValidationError
# from datetime import datetime

_logger = logging.getLogger(__name__)

class Product(models.Model):
    _inherit='product.product'

    def _website_price(self):
        qty = self._context.get('quantity', 1.0)
        partner = self.env.user.partner_id
        current_website = self.env['website'].get_current_website()
        pricelist = current_website.get_current_pricelist()
        company_id = current_website.company_id

        context = dict(self._context, pricelist=pricelist.id, partner=partner)
        self2 = self.with_context(context) if self._context != context else self

        ret = self.env.user.has_group('sale.group_show_price_subtotal') and 'total_excluded' or 'total_included'

        for p, p2 in pycompat.izip(self, self2):
            taxes = partner.property_account_position_id.map_tax(p.sudo().taxes_id.filtered(lambda x: x.company_id == company_id))
            p.website_price = taxes.compute_all(p2.price, pricelist.currency_id, quantity=qty, product=p2, partner=partner)[ret]
            # We must convert the price_without_pricelist in the same currency than the
            # website_price, otherwise the comparison doesn't make sense. Moreover, we show a price
            # difference only if the website price is lower

            ppis = p.product_tmpl_id.item_ids
            sales_pricelist = False
            for ppi in ppis:
                print(">>>>>>>>>>>>>>>>>>>>>>>>>>ppi", ppi.name, ppi.fixed_price)
                if ppi.min_quantity == 0 and ppi.date_start == False and ppi.date_end == False and ppi.pricelist_id.id == pricelist.id:
                    sales_pricelist = ppi.fixed_price

            if sales_pricelist:
                price_without_pricelist = sales_pricelist
            else:
                price_without_pricelist = p.list_price
            if company_id.currency_id != pricelist.currency_id:
                price_without_pricelist = company_id.currency_id.compute(price_without_pricelist, pricelist.currency_id)
            price_without_pricelist = taxes.compute_all(price_without_pricelist, pricelist.currency_id)[ret]
            p.website_price_difference = True if float_compare(price_without_pricelist, p.website_price, precision_rounding=pricelist.currency_id.rounding) > 0 else False
            if sales_pricelist:
                p.website_public_price = taxes.compute_all(price_without_pricelist, quantity=qty, product=p2, partner=partner)[ret]
            else:
                p.website_public_price = \
                    taxes.compute_all(p2.lst_price, quantity=qty, product=p2, partner=partner)[ret]