# -*- coding: utf-8 -*-

{
    "name": "Bista Maq Custom Fields",
    "version": "1.0",
    "author": "Bista Solutions Pvt. Ltd.",
    "maintainer": "Bista Solutions Pvt. Ltd.",
    "website": "https://www.bistasolutions.com",
    "category": "Custom",
    "license": "AGPL-3",
    'summary': 'This module adds two extra fields, One in Sale order named Cost and another in Delivery order picking line named Vendor Code.',
    'description': """In this module, we have added two fields in two different objects: - 
            1) A custom cost field in sale order lines object to display cost price according to company.
            2) A vendor code field on stock moves object to display vendor code set in vendor pricelist.""",
    "depends": ['sale', 'stock', 'sale_margin'],
    "data": [
        "views/sale_order_view_inherit.xml",
        "views/stock_picking_view_inherit.xml",
    ],
    "installable": True,
    "application": True,
}
