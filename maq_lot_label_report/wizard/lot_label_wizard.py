# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class LotLabelWizard(models.TransientModel):
    _name = 'lot.label.report.wizard'

    @api.model
    def default_get(self, field_vals):
        res = super(LotLabelWizard, self).default_get(field_vals)
        if res.get('label_type') == 'product' and self.env.context.get('active_model') == 'product.product':
            products = self.env['product.product'].browse(
                self.env.context.get('active_ids', []))
            res['product_lot_label_ids'] = [(0, 0, {'product_id': p.id, 'lot_ids': self.env['stock.production.lot'].sudo(
            ).search([('product_id', '=', p.id)]).ids, 'print_qty': 1}) for p in products]
        elif res.get('label_type') == 'production' and self.env.context.get('active_model') == 'stock.production.lot':
            stock_production_lots = self.env['stock.production.lot'].browse(
                self.env.context.get('active_ids', []))
            res['product_lot_label_ids'] = [
                (0, 0, {'product_id': s.product_id.id, 'lot_id': s.id, 'print_qty': 1}) for s in stock_production_lots]
        return res

    label_formats = fields.Selection([('f1v1', '4W x 20L v1 (Product Variant Internal Reference, GOVT SKU, Lot/Serial Number, LOT # Barcode)'),
                                      ('f2v1', '2W x 5L v1 (Product Variant Display Name, GOVT SKU, Lot/Serial Number, LOT # Barcode)')], string="Report Formats", default="f1v1")

    label_type = fields.Selection([('production', 'Production'),
                                   ('product', 'Product')])

    product_lot_label_ids = fields.One2many(
        'product.print.lot.label', 'wizard_id', string='Products')

    @api.multi
    def print_lot_report(self):
        self.ensure_one()
        data = {'ids': self.env.context.get('active_ids', [])}
        res = self.read()
        res = res and res[0] or {}
        data.update({'form': res})
        report = 'maq_lot_label_report.report_production_lot_label'
        if self.label_type == 'product':
            report = 'maq_lot_label_report.report_product_label'
        data['form']['pqty_by_product'] = {
            p.product_id.id: p.print_qty for p in self.product_lot_label_ids}
        data['form']['lotid_by_product'] = {
            p.lot_id.id : p.print_qty for p in self.product_lot_label_ids}
        data['form']['lot_by_product'] = {
            p.product_id.id: p.lot_ids.ids for p in self.product_lot_label_ids}
        return self.env.ref(report).with_context(from_transient_model=True).report_action([], data=data)


class ProductPrintLotLabel(models.TransientModel):
    _name = 'product.print.lot.label'

    product_id = fields.Many2one('product.product', string='Product')
    lot_ids = fields.Many2many("stock.production.lot", string="Lots")
    lot_id = fields.Many2one("stock.production.lot", string="Lot")
    print_qty = fields.Integer(default=1)
    wizard_id = fields.Many2one('lot.label.report.wizard')
