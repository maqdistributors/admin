# -*- coding: utf-8 -*-
{
    'name': "Ecommerce Category",

    'summary': "Adding a rule to allow/disallow categories of products by website",

    'description': "Adding a rule to allow/disallow categories of products by website",

    'author': "Odoo",
    'website': "http://www.odoo.com",

    'category': 'Odoo Customied App',
    'version': '1.2',

    'depends': [
        'website_sale',
        'im_livechat'
    ],
    'data': [
        'security/security.xml',
        'views/res_config_settings_views.xml',
        'views/views.xml',
        'views/res_users.xml',
        'views/templates.xml',
        'views/website_views.xml',
        'views/hide_pricing_template.xml',
        # emali debranding files
        # 'data/sale_mail_template_data.xml',
        # 'data/account_mail_template_data.xml',
        # 'data/purchase_mail_template_data.xml',
        #Delivery is not enable in prod 
        #'data/delivery_mail_template_data.xml'
    ],
}