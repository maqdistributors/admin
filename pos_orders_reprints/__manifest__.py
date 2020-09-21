# -*- coding: utf-8 -*-

{
    'name': 'POS Order Reprint',
    'version': '1.0',
    'category': 'Point of Sale',
    'sequence': 6,
    'author': 'WebVeer',
    'summary': "This module allows you to reprint the receipt by posbox thermal printer and normal printer." ,
    'description': """

=======================

This module allows you to reprint the receipt by posbox thermal printer and normal printer.

""",
    'depends': ['pos_orders_lists'],
    'data': [
        'views/views.xml',
        'views/templates.xml',
    ],
    'qweb': [
        'static/src/xml/pos.xml',
    ],
    'images': [
        'static/description/print.jpg',
    ],
    'installable': True,
    'website': '',
    'auto_install': False,
    'price': 10,
    'currency': 'EUR',
}
