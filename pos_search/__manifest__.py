# -*- coding: utf-8 -*-

{
    'name': 'POS Search',
    'version': '1.0',
    'category': 'Point Of Sale',
    'summary': 'Improves a product search in POS',
    'description': """This module allows user to search product in POS based on
    - Internal Reference
    - Product Name
    - Product Category
    - Barcode""",
    'author': 'Bista Solutions India Pvt Ltd.',
    'depends': ['point_of_sale'],
    'data': ['views/assets.xml'],
    'qweb': ['static/src/xml/pos_search.xml'],
    'installable': True,
    'auto_install': False
}
