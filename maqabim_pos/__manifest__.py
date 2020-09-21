# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    "name": "Maqabim Distributors: Point Of Sale customizations",
    'summary': "Point Of Sale customizations",
    'description': """
Maqabim Distributors: Point Of Sale customizations
==================================================
* Show internal reference of the product in the following POS views:
    - In main product view of the POS session
    - Once a product has been added to the order, on the list view on the left side, we need to have the internal reference shows as well On the POS receipt
* Taxes in POS
    - We want to see the total untaxed amount in the POS in the left side of the screen when products are selected
    - Within this view, we want the totals to show up in the following order:
        Subtotal
        Taxes
        Total
        These totals need to also show up on the POS receipt
    - Regarding the taxes, we need to show taxes per Tax group.
        So if multiple taxes apply to the order, we need in the tax totals to see one line per tax group. This is standard behavior on the sales order PDF. We need it to work  in the following views:
        - On the left side of the screen once we have chosen the product
        - On the receipt
    - Hide the tax setting button in the POS configuration
""",
    "author": "Odoo Inc",
    'website': "https://www.odoo.com",
    'category': 'Custom Development',
    'version': '0.1',
    'depends': ['point_of_sale'],
    'data': [
        'views/templates.xml',
    ],
    'qweb': ['static/src/xml/pos.xml'],
    'license': 'OEEL-1',
}
