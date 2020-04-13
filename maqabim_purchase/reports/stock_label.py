# -*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models, _
from odoo.exceptions import UserError


class ReportPickingLabel(models.AbstractModel):
    _name = 'report.maqabim_purchase.report_pickinglabel'

    @api.model
    def _get_report_values(self, docids, data=None):
        if not data.get('form'):
            raise UserError(_("Form content is missing, this report cannot be printed."))

        picking_ids = self.env.context.get('active_ids', [])
        pickings = self.env['stock.picking'].browse(picking_ids)
        report_format = data['form'].get('formats')
        return {
            'doc_ids': picking_ids,
            'doc_model': 'stock.picking',
            'docs': pickings,
            'data': data,
            'report_format': report_format
        }
