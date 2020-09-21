# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

{
    "name": "Bista Product Price",
    "version": "11.0.1.0.0",
    "author": "Bista Solutions Pvt. Ltd.",
    "maintainer": "Bista Solutions Pvt. Ltd.",
    "website": "https://www.bistasolutions.com",
    "category": "Web",
    "license": "AGPL-3",
    'summary': """This module contains following features
                1. Auto get price from pricelist as per start date, end date and active base.""",
    "depends": [
        "website_sale",
        "product",
        "sale"
    ],
    "data": [
        "views/product_template_views.xml",
    ],
    #    "qweb": [
    #        "static/src/xml/website_sale.xml",
    #    ],
    # "images": ["static/description/groupexpand.png"],
    "installable": True,
    "post_init_hook": "_update_sales_pricelist",
}

