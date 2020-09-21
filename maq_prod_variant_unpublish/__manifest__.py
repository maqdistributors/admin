# -*- coding: utf-8 -*-

{
    'name': 'Product Variant Show/Hide',
    'version': '1.0',
    'summary': 'Show or Hide Product Variant on the website shop',
    'description': "This module will be used to unpublish the product variant and/or hide the product variant from the website product page.",
    'depends': ['product', 'sale', 'website_sale'],
    'category': 'Sale',
    'data': [
        'views/product_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
