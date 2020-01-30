# -*- coding: utf-8 -*-

{
    "name": "Bista Maq Credit Note Pricelist",
    "version": "1.0",
    "author": "Bista Solutions Pvt. Ltd.",
    "maintainer": "Bista Solutions Pvt. Ltd.",
    "website": "https://www.bistasolutions.com",
    "category": "Custom",
    "license": "AGPL-3",
    'description': """In Customer Credit Note, consider Pricelist in order to calculate correct unit price in Customer invoice line""",
    'summary': '',
    "depends": ['account', ],
    "data": [
        "views/account_invoice_view.xml"
    ],
    "installable": True,
    "application": True,
}
