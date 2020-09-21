# -*- coding: utf-8 -*-

{
    "name": "Bista Maq Picking Box Number",
    "version": "1.0",
    "author": "Bista Solutions Pvt. Ltd.",
    "maintainer": "Bista Solutions Pvt. Ltd.",
    "website": "https://www.bistasolutions.com",
    "category": "Custom",
    "license": "AGPL-3",
    'summary': '''A box number character field is added in stock picking when operation type is delivery order and
                the same field is added in delivery slip report''',
    'description': """
    	Following features will be added
    	Req Id. 1.40 - Add custom field in Shipment operation & Delivery slip report""",
    "depends": ['stock'],
    "data": [
        "views/stock_picking_inherit_view.xml",
        "views/report_delivery_slip_inherit.xml",
    ],
    "installable": True,
    "application": True,
}
