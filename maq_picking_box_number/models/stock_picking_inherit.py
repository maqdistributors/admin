# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class StockMove(models.Model):
    _inherit = 'stock.move'

    '''Added Box number field in stock.move model'''

    m_box_number = fields.Char(string="Box Number")
