# -*- coding: utf-8 -*-

from odoo import models, fields, api


class StockMoveLine(models.Model):

    _inherit = 'stock.move.line'

    @api.depends('location_id', 'location_dest_id')
    def _get_m_warehouse_id(self):
        """
        If source location type is internal then warehouse id will be set from source location
        or if destination location type is internal then warehouse id will be set from destination location
        """
        for rec in self:
            if rec.location_id.usage == 'internal':
                rec.m_warehouse_id = rec.location_id.get_warehouse().id
            elif rec.location_dest_id.usage == 'internal':
                rec.m_warehouse_id = rec.location_dest_id.get_warehouse().id

    m_warehouse_id = fields.Many2one(
        "stock.warehouse", compute='_get_m_warehouse_id', string="Warehouse", store=True)
