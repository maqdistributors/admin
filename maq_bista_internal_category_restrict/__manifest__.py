# -*- coding: utf-8 -*-
{
    'name': 'MAQ Internal Category Product Restriction',
    'version': '1.0',
    'summary': 'User level product category selection and category related product restriction.',
    'description': """
    In this module, we will restrict the products which are related to product categories which are restricted
    for a particular user.
    """,
    'category': 'Sales',
    'website': 'https://www.bistasolutions.com/',
    'depends': ['sale'],
    'data': [
        'security/internal_category_security.xml',
        'views/assets.xml',
        'views/res_users_view.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
# Part of Odoo. See LICENSE file for full copyright and licensing details.