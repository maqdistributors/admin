# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class LabelReportWizard(models.TransientModel):

    _name = 'label.report.wizard'
    _description = 'Label Report'

    @api.model
    def default_get(self, field_vals):
        res = super(LabelReportWizard, self).default_get(field_vals)
        if res.get('label_type') == 'product' and self.env.context.get('active_model') == 'product.product':
            products = self.env['product.product'].browse(self.env.context.get('active_ids', []))
            res['product_label_ids'] = [(0, 0, {'product_id': p.id, 'print_qty': 1}) for p in products]
        return res

    formats = fields.Selection([
        ('f1_v1', '4W x 20L v1 (internal reference, sales price, barcode)'),
        ('f1_v2', '4W x 20L v2 (internal reference, barcode)'),
        ('f2_v1', '2W x 5L v1 (internal reference, barcode)'),
        ('f2_v2', '2W x 5L v2 (display name, barcode)')
    ], string='Report Formats', default='f1_v1')

    label_type = fields.Selection([
        ('sale', 'Sale'),
        ('purchase', 'Purchase'),
        ('picking', 'Picking'),
        ('product', 'Product')])
    product_label_ids = fields.One2many('product.print.label', 'wizard_id', string='Products')

    @api.multi
    def print_report(self):
        self.ensure_one()
        data = {'ids': self.env.context.get('active_ids', [])}
        res = self.read()
        res = res and res[0] or {}
        data.update({'form': res})
        report = 'maqabim_purchase.report_po_label'
        if self.label_type == 'sale':
            report = 'maqabim_purchase.report_so_label'
        elif self.label_type == 'picking':
            report = 'maqabim_purchase.report_picking_label'
        elif self.label_type == 'product':
            report = 'maqabim_purchase.report_product_label'
            data['form']['pqty_by_product'] = {p.product_id.id: p.print_qty for p in self.product_label_ids}
        return self.env.ref(report).with_context(from_transient_model=True).report_action([], data=data)


class ProductPrintLabel(models.TransientModel):
    _name = 'product.print.label'

    product_id = fields.Many2one('product.product', string='Product')
    print_qty = fields.Integer(default=1)
    wizard_id = fields.Many2one('label.report.wizard')
