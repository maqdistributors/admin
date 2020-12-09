# -*- coding: utf-8 -*-

{
    'name': 'Shopify Connector',
    'category': 'Odoo Connector',
    'summary': 'Publish your products on Shopify and creation of orders in Odoo.',
    'version': '1.0',
    'author': 'Bista Solutions',
    'website': 'http://www.bistasolutions.com',
    'license': 'AGPL-3',
    'description': """
Publish your products on Shopify as well as create and process an orders in Odoo
=============================

The Shopify integrator gives you the opportunity to manage your Odoo's products on Shopify.

Key Features
------------
* Publish products on Shopify
* Update inventory on Shopify
* Import of sales orders in Odoo and process invoices and delivery orders
""",
    'depends': [
        'product',
        'sale',
        'account',
        'sale_stock',
        # 'delivery',
    ],
    'data': [
        'security/shopify_connector_security.xml',
        'security/ir.model.access.csv',
        "views/partner_view.xml",
        "views/product_moves_view.xml",
        "views/product_uom_views.xml",
        "views/res_company_views.xml",
        "views/sale_order_and_sale_order_line_views.xml",
        "views/shopify_images_view.xml",
        "views/shopify_locations_view.xml",
        "views/shopify_metafields_view.xml",
        "views/shopify_order_error_log_view.xml",
        "views/shopify_prod_tags_view.xml",
        "views/product_views.xml",
        "wizard/export_shopify_product_variant.xml",
        "wizard/shopify_product_variant_sync_inventory_view.xml",
        "wizard/update_shopify_product_variant.xml",
        "views/shopify_product_product_view.xml",
        "wizard/export_shopify_product_template_view.xml",
        "wizard/update_shopify_product_template.xml",
        "wizard/shopify_import_orders_view.xml",
        "views/shopify_config_view.xml",
        "views/shopify_product_template_view.xml",
        "views/shopify_product_type_view.xml",
        "views/shopify_stock_object_views.xml",
        "views/shopify_vendor_view.xml",
        "views/shopify_menuitems.xml",
    ],
    'installable': True,
    'application': True,
    'post_init_hook': '_create_company_records',
}
