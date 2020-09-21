# -*- coding:utf-8 -*-

from odoo import api, models, _
from odoo.exceptions import UserError


class ReportProductionLotLabel(models.AbstractModel):
    _name = 'report.maq_lot_label_report.report_productionlotlabel'

    @api.model
    def _get_report_values(self, docids, data=None):
        if not data.get('form'):
            raise UserError(
                _("Form content is missing, this report cannot be printed."))

        production_lot_ids = self.env.context.get('active_ids', [])
        production_lots = self.env[
            'stock.production.lot'].browse(production_lot_ids)
        report_format = data['form'].get('label_formats')
        pqty_by_product = data['form'].get('pqty_by_product')
        lotid_by_product = data['form'].get('lotid_by_product')
        return {
            'doc_ids': production_lot_ids,
            'doc_model': 'stock.production.lot',
            'docs': production_lots,
            'data': data,
            'report_format': report_format,
            'pqty_by_product': pqty_by_product,
            'lotid_by_product': lotid_by_product
        }
