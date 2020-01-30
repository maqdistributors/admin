# -*- coding: utf-8 -*-

{
    "name": "Bista Maq Lot Label Report",
    "version": "1.0",
    "author": "Bista Solutions Pvt. Ltd.",
    "maintainer": "Bista Solutions Pvt. Ltd.",
    "website": "https://www.bistasolutions.com",
    "category": "Custom",
    "license": "AGPL-3",
    'summary': 'This module adds the facility to print lot label barcode printing for products.',
    'description': """In this module, we have added two report formats in two different objects: - 
            1) Lot Label Report menu in action menu for Lot/Serial number object.
            2) Lot Label Report menu in action menu for Product Variants object""",
    "depends": ['product', 'stock'],
    "data": [
        "views/product_views.xml",
        "wizard/lot_label_view.xml",
        "reports/lot_label_report_templates.xml",
        "reports/product_templates.xml",
        "reports/production_lot_templates.xml",
        "reports/reports.xml"

    ],
    "installable": True,
    "application": True,
}
