# -*- coding: utf-8 -*-

{
    'name': 'MAQ Sales Report Warehouse',
    'version': '1.0',
    'summary': 'Before creating a PO, MAQ always runs the sales report so they can have an idea and create a PO properly with specific items and quantity',
    'description': """
    1.45 Report to show the On hand qty, Forecasted qty, Delivered qty based on provided by warehouse and vendor and date filter.
    """,
    "author": "Bista Solutions Pvt. Ltd.",
    "maintainer": "Bista Solutions Pvt. Ltd.",
    "website": "https://www.bistasolutions.com",
    'depends': ['stock'],
    'category': 'Warehouse',
    'data': [
        'security/sales_report_security.xml',
        'security/ir.model.access.csv',
        'views/custom_sales_report_view.xml',
        'views/shopify_warehouse_view.xml'
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
