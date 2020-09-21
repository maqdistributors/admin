# -*- coding: utf-8 -*-


from odoo import fields, models,tools,api, _

class pos_config(models.Model):
    _inherit = 'pos.config' 
    
    allow_load_orders = fields.Boolean("Allow Load Orders",default=True)
    wv_order_date = fields.Integer(string="Old Order days")
    wv_lodad_config = fields.Many2many('pos.config',"pos_config_config","config1","config2",string="Orders Config")
