# -*- coding: utf-8 -*-

{
    'name': 'POS Orders',
    'version': '1.0',
    'category': 'Point of Sale',
    'sequence': 6,
    'author': 'WebVeer',
    'summary': "This module allows you to show old orders." ,
    'description': """

=======================

This module allows you to show old orders.

""",
    'depends': ['point_of_sale'],
    'data': [
        # 'views/views.xml',
        'views/templates.xml',
    ],
    'qweb': [
        'static/src/xml/pos.xml',
    ],
    'images': [
        'static/description/dtl.jpg',
    ],
    'installable': True,
    'website': '',
    'auto_install': False,
    'price': 15,
    'currency': 'EUR',
}
