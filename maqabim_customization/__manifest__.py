# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    "name": "Maqabim Distributors: SO PDF custo + Sticky header for website",
    'summary': "Web",
    'description': """
Maqabim Distributors: SO PDF custo + Sticky header for website
===============================================================
- SO PDF custo + Sticky header for website
    - Delivered' and 'Invoiced quantity SO PDF
    - sticky header
""",
    "author": "Odoo Inc",
    'website': "https://www.odoo.com",
    'category': 'Custom Development',
    'version': '0.1',
    'depends': ['sale_management', 'website'],
    'data': [
        'views/report_sale.xml',
        'views/templates.xml'
    ],
    'license': 'OEEL-1',
}