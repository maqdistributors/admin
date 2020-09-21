# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Inventory Access Customization',
    'description': """
    - Block price and cost
    """,
    'category': 'Stock',
    'depends': ['stock', 'purchase'],
    'data': [
        'views/product_view.xml',
        ],
    'license': 'OEEL-1',
    'installable': True,
}
