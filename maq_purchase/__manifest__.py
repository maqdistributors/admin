# -*- coding: utf-8 -*-

{
    'name': 'Maq Purchase Amount Grouping',
    'version': '1.0',
    'summary': 'The module applies group on unit price total price and subtotal fields ',
    'description': """
    Following features will be added

    Req Id. 1.89 - Show vendor specific products in PO Line
    Req Id. 1.90 - Add custom field in PO for the Joint PO process
    """,
    'depends': ['purchase'],
    'category': 'Purchase',
    'data': [
        'security/purchase_amount_security.xml',
        'views/purchase_order_inherit_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
