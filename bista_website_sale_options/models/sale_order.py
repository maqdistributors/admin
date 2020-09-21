# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    '''Added new website comment field in sale order'''
    m_website_comment = fields.Text('Comment on website page')
