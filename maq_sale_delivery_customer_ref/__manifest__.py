# -*- coding: utf-8 -*-

{
    'name': 'MAQ Customer Reference Sale Delivery',
    'version': '1.0',
    'summary': 'Add customer reference in sales order and delivery order.',
    'description': """
    Following feature will be added
    1.96 Set customer reference from So to Pick/Pack Shipment""",
    'depends': ['sale', 'stock', 'sale_stock'],
    'category': 'Sale',
    'data': ['views/sale_view.xml'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
