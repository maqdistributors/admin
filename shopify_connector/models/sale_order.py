# -*- coding: utf-8 -*-

from odoo import models, fields, api
from lxml import etree


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    shopify_name = fields.Char(
        "Shopify Name", help="Enter Shopify Name", track_visibility='onchange', readonly=True)
    shopify_order_id = fields.Char(
        "Shopify Order ID", help="Enter Shopify Order ID", track_visibility='onchange', readonly=True)
    shopify_note = fields.Char(
        "Shopify Note", help="Enter Shopify Note", track_visibility='onchange', readonly=True)
    shopify_fulfillment_status = fields.Char(
        "Shopify Fulfillment Status", help="Enter Shopify Fulfillment Status", track_visibility='onchange', readonly=True)
    shopify_financial_status = fields.Char(
        "Shopify Financial Status", help="Enter Shopify Financial Status", track_visibility='onchange', readonly=True)
    shopify_import_status = fields.Selection([('successfull_import', 'Successfully Imported'), ('fail_to_create_do', 'Failed to Create Delivery Order'), (
        'fail_to_create_invoice', 'Failed To Create Invoice'), ('other', 'Other')], "Shopify Import Status", help="Enter Shopify Import Status", track_visibility='onchange', readonly=True)
    shopify_error_message = fields.Char(
        "Shopify Error Message", help="Enter Shopify Error Message", track_visibility='onchange', readonly=True)
    shopify_config_id = fields.Many2one(
        "shopify.config", "Shopify Config", readonly=True)

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        '''
        Hide create and delete ability when we get shopify_sale_order in context
        '''
        res = super(SaleOrder, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        if view_type == 'tree' and self._context.get('shopify_sale_order'):
            doc = etree.XML(res['arch'])
            for node in doc.xpath("//tree"):
                if self._context['shopify_sale_order'] == 1:
                    node.set('create', "false")
                    node.set('delete', 'false')
                else:
                    node.set('create', "true")
                    node.set('delete', 'true')
            res['arch'] = etree.tostring(doc, encoding='unicode')
        if view_type == 'form' and self._context.get('shopify_sale_order'):
            doc = etree.XML(res['arch'])
            for node in doc.xpath("//form"):
                if self._context['shopify_sale_order'] == 1:
                    node.set('create', "false")
                    node.set('delete', 'false')
                else:
                    node.set('create', "true")
                    node.set('delete', 'true')
            res['arch'] = etree.tostring(doc, encoding='unicode')
        return res

    @api.multi
    def action_invoice_create(self, grouped=False, final=False):
        '''
        Inherit this method to improve the discount price according to invoiced quantities to set exact discount amount
        '''
        res = super(SaleOrder, self).action_invoice_create(grouped, final)
        account_invoice_id = res[0]
        ordered_qty = 0
        invoiced_qty = 0
        discount_amount = 0
        final_discount_amount = 0
        inv_qty_subtotal = 0
        order_qty_subtotal = 0
        discount_percentage = 0
        account_invoice_obj = self.env['account.invoice'].browse(account_invoice_id)
        invoice_lines = account_invoice_obj.invoice_line_ids
        for order in self:
            order_discount_product = order.order_line.filtered(lambda l: l.product_id.shopify_discount_product)
            if order._context.get('partial_fulfill_refund_order') and order_discount_product.name == 'fixed_amount':
                for line in invoice_lines:
                    if line.product_id.shopify_discount_product:
                        discount_amount += line.price_unit
                    if not line.product_id.shopify_discount_product and not line.product_id.shopify_shipping_product:
                        ordered_qty += line.ordered_qty
                        invoiced_qty += line.quantity
                final_discount_amount += (invoiced_qty * discount_amount)/ordered_qty
                inv_discount_product = invoice_lines.filtered(lambda i: i.product_id.shopify_discount_product)
                inv_discount_product.price_unit = final_discount_amount
            elif order._context.get('partial_fulfill_refund_order') and order_discount_product.name == 'percentage':
                for line in invoice_lines:
                    if line.product_id.shopify_discount_product:
                        discount_amount += line.price_unit
                    if not line.product_id.shopify_discount_product and not line.product_id.shopify_shipping_product:
                        inv_qty_subtotal += line.price_unit * line.quantity
                        order_qty_subtotal += line.price_unit * line.ordered_qty
                discount_percentage = (discount_amount * 100)/order_qty_subtotal
                final_discount_amount += (inv_qty_subtotal * discount_percentage)/100
                final_discount_amount = str(final_discount_amount)
                final_discount_amount_split_list = final_discount_amount.split(".")
                final_discount_amount = final_discount_amount_split_list[0] + "." + final_discount_amount_split_list[1][:2]
                final_discount_amount = float(final_discount_amount)
                inv_discount_product = invoice_lines.filtered(lambda i: i.product_id.shopify_discount_product)
                inv_discount_product.price_unit = final_discount_amount
        #Explicitly compute Tax against invoice
        account_invoice_obj.compute_taxes()
        return res


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    shopify_order_line_id = fields.Char(
        "Shopify Order Line ID", help="Enter Shopify Order Line ID", track_visibility='onchange', readonly=True)
