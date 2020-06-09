# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': "Maqabim Website Popup",
    'summary': """Maqabim Website Popup""",
    'sequence': 100,
    'license': 'OEEL-1',
    'website': 'https://www.odoo.com',
    'version': '1.0',
    'author': 'Odoo Inc',
    'description': """
Maqabim Website Popup
=====================
* By clicking Enter, you are consenting to your State or Province's Laws.
* This website may contain smoking and smoking alternative products.
    """,
    'category': 'Custom Development',
    'depends': ['website'],
    'data': [
        'views/website_template.xml',
    ],
    'demo': [],
    'qweb': ['static/src/xml/*.xml'],
    'installable': True,
    'application': False,
    'auto_install': False,
}
