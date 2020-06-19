# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

{
    "name": "Bista Website Sortby New Product",
    "version": "11.0.1.0.0",
    "author": "Bista Solutions Pvt. Ltd.",
    "maintainer": "Bista Solutions Pvt. Ltd.",
    "website": "https://www.bistasolutions.com",
    "category": "Web",
    "license": "AGPL-3",
    'summary': """This module contains following features
                1. Add new feature for sort by new product.""",
    "depends": [
        "website_sale",
        "product"
    ],
    "data": [
        "views/product_template_views.xml",
        "views/templates.xml"
    ],
    #    "qweb": [
    #        "static/src/xml/website_sale.xml",
    #    ],
    # "images": ["static/description/groupexpand.png"],
    "installable": True,
    "application": True,
    "post_init_hook": "_update_publish_date",
}

