# -*- coding: utf-8 -*-

{
    'name': 'MAQ Inventory Adjustment',
    'version': '1.0',
    'summary': 'Extra filters added for Inventory adjustment',
    'description': """Following features will be added
    Req Id. 1.42 - Reverse Shipment information for processing
    Req Id. 1.98 - Approval process for inventory adjustment
    Req Id. 2.00 - Set the checkbox ticked by default
    """,
    'depends': ['stock', 'website_sale', 'stock_account'],
    'category': 'Warehouse',
    'data': [
        'security/maq_security.xml',
        'security/ir.model.access.csv',
        'views/stock_inventory_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
