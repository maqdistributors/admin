# -*- coding: utf-8 -*-

{
    'name': 'Pos order return',
    'version': '1.0',
    'category': 'Point of Sale',
    'sequence': 6,
    'author': 'Webveer',
    'summary': 'Easy way to return order from point of sale',
    'description': """

=======================

Easy way to return products from point of sale.

""",
    'depends': ['pos_orders_lists'],
    'data': [
        'views/views.xml',
        'views/templates.xml'
    ],
    'qweb': [
        'static/src/xml/pos.xml',
    ],
    'images': [
        'static/description/popup.jpg',
    ],
    'installable': True,
    'website': '',
    'auto_install': False,
    'price': 25,
    'currency': 'EUR',
}
