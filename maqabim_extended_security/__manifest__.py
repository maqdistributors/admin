# -*- coding: utf-8 -*-
{
    "name": "Maqabim Distributors: Custom access rights",
    'summary': "Web",
    'description': """
Maqabim Distributors: Custom access rights
==========================================

""",
    "author": "Odoo Inc",
    'website': "https://www.odoo.com",
    'category': 'Custom Development',
    'version': '0.1',
    'depends': ['point_of_sale', 'maqabim_sale', 'stock', 'website', 'maqabim_purchase'],
    'data': [
        'security/security_groups.xml',
        'security/ir.model.access.csv',
        'views/res_users_views.xml',
        'views/point_of_sale_views.xml',
        'views/purchase_views.xml'
    ],
    'license': 'OEEL-1',
}