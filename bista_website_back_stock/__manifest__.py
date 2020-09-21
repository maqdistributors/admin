# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

{
    "name": "Bista Website Back In Stock",
    "version": "12.0.1.0.0",
    "author": "Bista Solutions Pvt. Ltd.",
    "maintainer": "Bista Solutions Pvt. Ltd.",
    "website": "https://www.bistasolutions.com",
    "category": "Web",
    "license": "AGPL-3",
    'summary': """This module contains following features
                1. Display back in stock products.""",
    "depends": [
        "website_sale",
        "product",
        "bista_website_sortby_new"
    ],
    "data": [
        "views/website_sale.xml",
        "views/product_template_views.xml",
    ],
    #    "qweb": [
    #        "static/src/xml/website_sale.xml",
    #    ],
    # "images": ["static/description/groupexpand.png"],
    "installable": True,
    "post_init_hook": "_update_back_in_stock",
}

