# -*- coding: utf-8 -*-

{
    'name': 'MAQ Sale Order Line Editable',
    'version': '1.0',
    'summary': 'Keep Sale Order Line editable in all scenarios while creating the sale order and product in sale order lines',
    'description': """Following Sale Order features will be added
                      Req Id. 1.44 - Make Sale Order Line edtiable bottom like PO and Invoice lines.
                      User can edit the Sale order lines just like purchase order lines""",
    'depends': ['sale'],
    'category': 'Sale',
    'data': ['views/sale_order_view.xml'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
