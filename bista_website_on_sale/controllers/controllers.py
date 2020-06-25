# -*- coding: utf-8 -*-
import json
import logging
from werkzeug.exceptions import Forbidden, NotFound

from odoo import http, tools, _
from odoo.http import request
from odoo.addons.base.ir.ir_qweb.fields import nl2br
from odoo.addons.http_routing.models.ir_http import slug
from odoo.addons.website.controllers.main import QueryURL
from odoo.exceptions import ValidationError
from odoo.addons.website.controllers.main import Website
from odoo.addons.website_form.controllers.main import WebsiteForm
from odoo.osv import expression
from odoo.addons.website_sale.controllers.main import WebsiteSale, TableCompute
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)

PPG = 28  # Products Per Page
PPR = 4   # Products Per Row

class WebsiteSale(WebsiteSale):

    @http.route([
        '/sale',
        '/sale/page/<int:page>'
    ], type='http', auth="public", website=True)
    def sale(self, page=0, category=None, search='', ppg=False, **post):
        current_website = request.env['website'].get_current_website()
        if current_website.website_shop_login and (request.env.user._is_public() or request.env.user.id == request.website.user_id.id):
            redirect_url = '/web/login?redirect=%s'%(request.httprequest.url)
            if current_website.website_shop_login_redirect:
                redirect_url = '%s?redirect=%s'%(current_website.website_shop_login_redirect, request.httprequest.url)
            else:
                # redirct user to /web/signup if b2c signup is enable
                if current_website.website_auth_signup_uninvited == 'b2c':
                    redirect_url = '/web/signup?redirect=%s'%(request.httprequest.url)
            return request.redirect(redirect_url)

        if ppg:
            try:
                ppg = int(ppg)
            except ValueError:
                ppg = PPG
            post["ppg"] = ppg
        else:
            ppg = PPG

        if category:
            category = request.env['product.public.category'].search([('id', '=', int(category))], limit=1)
            if not category:
                raise NotFound()

        attrib_list = request.httprequest.args.getlist('attrib')
        attrib_values = [[int(x) for x in v.split("-")] for v in attrib_list if v]
        attributes_ids = {v[0] for v in attrib_values}
        attrib_set = {v[1] for v in attrib_values}

        domain = self._get_search_domain(search, category, attrib_values)

        keep = QueryURL('/sale', category=category and int(category), search=search, attrib=attrib_list, order=post.get('order'))

        compute_currency, pricelist_context, pricelist = self._get_compute_currency_and_context()

        request.context = dict(request.context, pricelist=pricelist.id, partner=request.env.user.partner_id)

        url = "/sale"
        if search:
            post["search"] = search
        if attrib_list:
            post['attrib'] = attrib_list

        categs = request.env['product.public.category'].search([('parent_id', '=', False),('website_id','=',request.context['website_id'])])        
        Product = request.env['product.template']

        parent_category_ids = []
        if category:
            url = "/sale/category/%s" % slug(category)
            parent_category_ids = [category.id]
            current_category = category
            while current_category.parent_id:
                parent_category_ids.append(current_category.parent_id.id)
                current_category = current_category.parent_id

        sale_product_id = []

        sale_product = False

        if pricelist:

            pricelist_items = pricelist.item_ids

            for pricelist_item in pricelist_items:

                applied_on = pricelist_item.applied_on
                date_start = pricelist_item.date_start
                date_end = pricelist_item.date_end
                date_start_date = datetime.now().date() - timedelta(days=100)
                date_end_date = datetime.now().date() - timedelta(days=100)

                if date_start and date_end:
                    date_start_date = datetime.strptime(date_start, '%Y-%m-%d').date()
                    date_end_date = datetime.strptime(date_end, '%Y-%m-%d').date()

                if applied_on == '1_product':
                    sale_product = pricelist_item.product_tmpl_id.id
                    if pricelist_item.min_quantity in [0,1] and pricelist_item.date_start == False and pricelist_item.date_end == False:
                        continue
                    elif pricelist_item.min_quantity > 1 and pricelist_item.date_start == False and pricelist_item.date_end == False:
                        continue
                    elif pricelist_item.min_quantity in [0,1] and pricelist_item.date_end:
                        if (date_start_date == datetime.now().date() or date_start_date < datetime.now().date()) and (
                                    date_end_date == datetime.now().date() or date_end_date > datetime.now().date()):
                            sale_product_id.append(sale_product)
                        else:
                            continue
                    else:
                        sale_product_id.append(sale_product)

        # domain += [('public_categ_ids','child_of', [x.id for x in categs]),('id', 'in', sale_product_id)]


        # domain += [('public_categ_ids', 'child_of', [x.id for x in categs])]

        # product_count = Product.search_count(domain)
        #
        # pager = request.website.pager(url=url, total=product_count, page=page, step=ppg, scope=7, url_args=post)
        #
        # products = Product.search(domain, limit=ppg, offset=pager['offset'], order=self._get_search_order(post))

        company_id = current_website.company_id.id
        node_field = False
        product_list = []
        order = post.get('order')

        if order:

            node = order.split(" ")

            if node[0]:
                node_field = node[0]

        elif order == None:

            post['order'] = "publish_date desc"
            node_field = "publish_date"

        if node_field == 'sales_pricelist' or node_field == 'publish_date':
            product_list_values = self._company_dependent_order_by_sale(company_id, Product, categs, domain, sale_product_id, url, page, ppg,
                                                                   post)
            product_list = product_list_values.get('product_list')
            product_count = product_list_values.get('product_count')
            pager = product_list_values.get('pager')

        if len(product_list) > 0:
            products = Product.browse(product_list)
        else:
            domain += [('public_categ_ids', 'child_of', [x.id for x in categs]),('id', 'in', sale_product_id)]
            product_count = Product.search_count(domain)
            pager = request.website.pager(url=url, total=product_count, page=page, step=ppg, scope=7, url_args=post)
            products = Product.search(domain, limit=ppg, offset=pager['offset'], order=self._get_search_order(post))

        ProductAttribute = request.env['product.attribute']
        if products:
            # get all products without limit
            selected_products = Product.search(domain, limit=False)
            attributes = ProductAttribute.search([('attribute_line_ids.product_tmpl_id', 'in', selected_products.ids)])
        else:
            attributes = ProductAttribute.browse(attributes_ids)

        values = {
            'search': search,
            'category': category,
            'attrib_values': attrib_values,
            'attrib_set': attrib_set,
            'pager': pager,
            'pricelist': pricelist,
            'products': products,
            'search_count': product_count,  # common for all searchbox
            'bins': TableCompute().process(products, ppg),
            'rows': PPR,
            'categories': categs,
            'attributes': attributes,
            'compute_currency': compute_currency,
            'keep': keep,
            'parent_category_ids': parent_category_ids,
        }
        if category:
            values['main_object'] = category
        return request.render("website_sale.products", values)

    def _company_dependent_order_by_sale(self, company_id, Product, categs, domain, sale_product_id, url, page, ppg, post):

        ir_property = request.env['ir.property']
        ir_property_ids = False
        ir_domain = []

        node = post.get('order').split(" ")
        node_field = node[0]
        node_order = node[1]

        if node_field and node_order:

            ir_domain += [('name', '=', node_field), ('company_id', '=', company_id)]

            if node_field == "publish_date":
                order = "value_datetime "+ str(node_order)
            else:
                order = "value_float " + str(node_order)

            if categs:
                domain += [('public_categ_ids', 'child_of', [x.id for x in categs]),('id', 'in', sale_product_id)]
                product_ids = Product.search(domain).ids

            res_ids = []
            for res_id in product_ids:
                res_ids.append('product.template,' + str(res_id))

            if len(res_ids) > 0:
                ir_domain += [('res_id', 'in', res_ids)]

            product_count = ir_property.search_count(ir_domain)
            pager = request.website.pager(url=url, total=product_count, page=page, step=ppg, scope=7, url_args=post)
            ir_property_ids = ir_property.search(ir_domain, limit=ppg, offset=pager['offset'], order=order)

        product_list = []
        if ir_property_ids:
            for ir_property_id in ir_property_ids:
                res_id = ir_property_id.res_id
                res_val = res_id.split(',')
                product_id = int(res_val[1])
                product = Product.search(
                    ['&', ('id', '=', product_id), '|', ('company_id', '=', False), ('company_id', '=', company_id)])
                if product.id != False:
                    product_list.append(product.id)

        return {"product_list":product_list, "product_count":product_count, "pager":pager}
