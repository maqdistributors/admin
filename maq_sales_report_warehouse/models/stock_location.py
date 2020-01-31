# -*- coding: utf-8 -*-

from odoo import models, fields, api


class StockLocation(models.Model):

    _inherit = 'stock.location'

    #@api.depends('name','parent_left','parent_right','usage','location_id')
    @api.depends('name','usage','location_id')
    def _get_m_warehouse_id(self):
        """
        If source location type is internal then warehouse id will be set from source location
        or if destination location type is internal then warehouse id will be set from destination location
        """
        for rec in self:
            rec.m_warehouse_id = rec.get_warehouse().id

    m_warehouse_id = fields.Many2one("stock.warehouse", compute='_get_m_warehouse_id', string="Warehouse", store=True)
