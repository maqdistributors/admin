# -*- coding: utf-8 -*-
{
    'name': 'MAQ Point of Sale',
    'version': '11.0.1.0.0',
    'summary': 'Point of sale',
    'description': """
    Point of Sale Custom code
    """,
    'category': 'POS',
    'website': 'https://www.bistasolutions.com/',
    'depends': ['point_of_sale'],
    'data': [
        'views/assets.xml',
        'views/pos_config_view.xml',
        'views/pos_order_view.xml',
    ],
    'demo': [
    ],
    'qweb': ['static/src/xml/*.xml'],
    'installable': True,
    'application': False,
    'auto_install': False,
}
# Part of Odoo. See LICENSE file for full copyright and licensing details.
