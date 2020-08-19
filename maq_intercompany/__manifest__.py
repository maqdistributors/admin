# -*- coding: utf-8 -*-

{
    'name': 'Maq Intercompany',
    'category': 'Custom',
    'summary': 'Update a view as per company restrictions and make fields to be company dependent',
    'version': '1.0',
    'author': 'Bista Solutions',
    'website': 'http://www.bistasolutions.com',
    'license': 'AGPL-3',
    'description': """
Update a view as per company restrictions and make fields to be company dependent
=============================

1. User can see log notes of users from other companies about inter-company products
------------
2. Allow users to only see companies in the dropdown which they are allowed to access
------------

3. Following views are updated
------------
* Product Moves
* INVENTORY --> OPERATIONS --> SCRAP

4. Following fields will act as company dependent
------------
* Can be Sold
* Can be Purchased
* Sale Price
* Variant Prices
* Available in Point of Sale
* Control Policy
* Invoicing Policy
* Published on Website
* Manufacturing Lead Time
* Customer Lead Time
    """,
    'depends': [
        #'stock','product', 'website_multi', 'website_sale', 'ecommerce_category', 'sale_coupon',
        'stock','product', 'website_sale', 'ecommerce_category', 'sale_coupon', 'website_product_publish',
        'calendar'
    ],
    'data': [
        'security/intercompany_security.xml',
        'security/ir.model.access.csv',
        'views/delivery_slip_report_view_inherit.xml',
#         'views/product_attribute_price.xml',
        'views/product_public_categ_inherit.xml',
        'views/product_style_view.xml',
        'views/product_template_inherit.xml',
        'views/product_template_website_desc_view.xml',
    ],
    'installable': True,
    'application': True,
    'uninstall_hook': 'uninstall_hook',
}
