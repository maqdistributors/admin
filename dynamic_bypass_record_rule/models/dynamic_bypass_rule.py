# -*- coding: utf-8 -*-

from odoo import models, fields, api
active_model = {}


class DynamicBypassRule(models.Model):
    _name = 'dynamic.bypass.record.rule'
    _rec_name = 'model_id'

    model_id = fields.Many2one('ir.model', 'Select Main Model', copy=False,
                               help='Model on which you want to bypass the record rule.')
    model_ids = fields.Many2many('ir.model', string='Relational Models',
                                 help='Relational models for which you want to bypass the record rule.')

    @api.onchange('model_id')
    def onchange_model_id(self):
        self.model_ids = [(6, 0, [])]



class IrRule(models.Model):
    _inherit = 'ir.rule'

    @api.model
    def domain_get(self, model_name, mode='read'):
        res = super(IrRule, self).domain_get(model_name=model_name,
                                             mode=mode)
        global active_model
        if self._context.get('params') and self._context['params'].get('action'):
            act_id = self._context['params']['action']
            if isinstance(act_id, int):
                self._cr.execute('SELECT res_model FROM ir_act_window where id=%s', (act_id,))
                result = self._cr.fetchone()
                active_model.update({self._uid: result and result[0].encode('UTF-8') or ''})

        if active_model and self._uid in active_model:
            rule_obj = self.env['dynamic.bypass.record.rule']
            rule = rule_obj.sudo().search([('model_id.model', '=', active_model[self._uid])], limit=1)
            bypass_models = [x.model.encode('UTF-8') for x in rule.model_ids if rule]
            if model_name in bypass_models:
                return [], [], ['"' + self.pool[model_name]._table + '"']
        return res
