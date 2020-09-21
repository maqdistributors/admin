# -*- coding: utf-8 -*-
{
    'name': "Stock Performance",
    'summary': """
        Improve stock performance""",
    'description': """
        Rewrite main stock function with procurement in order
        to process them in batch instead of 1 by 1.
    """,
    'website': 'https://www.odoo.com/page/warehouse',
    'category': 'Warehouse',
    'version': '0.1',
    'sequence': 100,
    'depends': ['mrp', 'sale_stock'],
    'demo': [],
    'data': [],
    'installable': True,
    'auto_install': False,
}
