# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    "name": "Maqabim Distributors: Invoice customizations",
    'summary': "Web",
    'description': """
Maqabim Distributors: Invoice customizations
============================================
- on account invoice line showed the order quantity fetched from the sale order line.
""",
    "author": "Odoo Inc",
    'website': "https://www.odoo.com",
    'category': 'Custom Development',
    'version': '0.1',
    'depends': ['sale_management', 'account'],
    'data': [
        'views/account_invoice_views.xml',
        'views/report_invoice.xml',
        'views/portal_templates.xml'
    ],
    'license': 'OEEL-1',
}