# -*- coding: utf-8 -*-

{
    'name': 'Theme Search Bar',
    'category': 'Custom',
    'summary': 'Theme Search bar product list',
    'version': '11.0.1.0.0',
    'author': 'Bista Solutions',
    'website': 'http://www.bistasolutions.com',
    'license': 'AGPL-3',
    'description': """
    Theme Search bar product list
        """,
    'depends': [
        'website_sale',
        'bista_website_sale_options'
    ],
    'data': [
        'view/assets.xml',
        'view/header.xml'
    ],
    'installable': True,
    'application': True,
}
