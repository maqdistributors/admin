# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    "name": "Maqabim Distributors: Purchase customizations",
    'summary': "Purchase customizations",
    'description': """
Maqabim Distributors: Purchase customizations
=============================================
This module will added new report on PO for priting product label

-------------------
* TASK ID - 1957722
-------------------
1. On a PO (form view)
    - We need a custom action ‘Print PO-labels’ that will generate a PDF of the specified labels.
        - Next to the qty field in the PO-line we need a second field ‘Print Qty’
            - This field needs to get the same value as the ordered qty by default
            - However, the user should be able to adjust this qty so that the printed report prints that specified amount of labels
            - If one line initially states: Product = A : QTY = 10 : Print QTY = 10
                - And the user changes it to : Product = A : QTY = 10 : Print QTY = 2
                - We need this label to be printed 2 times
            - We need the labels to be ordered from left to right, top to bottom
            - Before printing, we need a wizard to pop up asking us what format we want to print in (see below in this spec the details on formats and types).

2. On an SO (form view)
    - We need a custom action ‘Print SO-labels’ that will generate a PDF of the specified labels.
        - Next to the qty field in the SO-line we need a second field ‘Print Qty’
            - This field needs to get the same value as the ordered qty by default
            - However, the user should be able to adjust this qty so that the printed report prints that specified amount of labels
            - If one line initially states: Product = A : QTY = 10 : Print QTY = 10
                - And the user changes it to : Product = A : QTY = 10 : Print QTY = 2
                - We need this label to be printed 2 times
            - We need the labels to be ordered from left to right, top to bottom
            - Before printing, we need a wizard to pop up asking us what format we want to print in (see below in this spec the details on formats and types)

3. On stock transfers (stock.picking) (form view)
    - We need a custom action ‘Print Picking Labels’ on a transfer (stock.picking) that will generate a PDF of the specified labels.
        - Next to the qty field in the picking line we need a second field ‘Print Qty’
            - This field needs to get the same value as the ordered qty by default
            - However, the user should be able to adjust this qty so that the printed report prints that specified amount of labels
            - If one line initially states: Product = A : QTY = 10 : Print QTY = 10
                - And the user changes it to : Product = A : QTY = 10 : Print QTY = 2
                - We need this label to be printed 2 times
            - We need the labels to be ordered from left to right, top to bottom
            - Before printing, we need a wizard to pop up asking us what format we want to print in (see below in this spec the details on formats and types).

4. On Product Variants (list view)

    - We need a custom action ‘Print Product Labels’ that will generate a PDF of the selected labels in list view.
        - Before printing, there needs to be a wizard that pops up which will ask the users the following:
            - Format (4 options listed below in this spec)
            - Qty
                - We need each selected product in the list view to also be listed in the wizard pop up.
                    - Next to each line we need a qty field which will have a default value of 1
                    - The user can manually adjust the qty of each line before printing the report.
                        - Example:
                            - I select 10 product variants in the list view, I click on the Print Product Labels action item.
                            - A wizard pops up with a field to select the format and 10 lines with a qty field next to each line
                            - All line items have prefilled qty = 1
                            - I manually adjust qty of the last 5 rows to 10
                            - I click print
                            - This prints 55 labels in total > 1 label for each of the first 5 products and 10 labels for each of the last 5.



""",
    "author": "Odoo Inc",
    'website': "https://www.odoo.com",
    'category': 'Custom Development',
    'version': '0.1',
    'depends': ['purchase', 'sale_stock'],
    'data': [
        'wizard/label_report_views.xml',

        'reports/label_report_template.xml',
        'reports/purchase_templates.xml',
        'reports/sale_templates.xml',
        'reports/stock_templates.xml',
        'reports/product_templates.xml',
        'reports/reports.xml',

        'views/purchase_views.xml',
        'views/sale_views.xml',
        'views/stock_views.xml',
    ],
    'license': 'OEEL-1',
}
