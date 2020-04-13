# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ShopifyMetafields(models.Model):
    _name = 'shopify.metafields'
    _description = 'Shopify Metafields'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _rec_name = 'key'

    key = fields.Char("Key", required=True, help="Enter Key",
                      track_visibility="onchange")
    value = fields.Char("Value", required=True, help="Enter Value",
                        track_visibility="onchange")
    value_type = fields.Selection({('string', 'string'),
                                   ('integer', 'integer'),
                                   ('json_string', 'json_string')},
                                  "Value Type", required=True, help="Enter Value Type",
                                  track_visibility="onchange")
    namespace = fields.Char(
        "Namespace", required=True, help="Enter Value Type", track_visibility="onchange")

    @api.multi
    def name_get(self):
        result = []
        for rec in self:
            result.append((rec.id, "%s/%s - %s" %
                           (rec.namespace, rec.key, rec.value)))
        return result

    @api.model
    def create(self, vals):
        res = super(ShopifyMetafields, self).create(vals)
        if vals.get('value_type') == 'integer':
            try:
                value = int(vals.get('value'))
            except ValueError:
                raise ValidationError(
                    _("Please enter integer value for integer type"))
        return res

    @api.multi
    def write(self, vals):
        res = super(ShopifyMetafields, self).write(vals)
        for rec in self:
            if vals.get('value_type') == 'integer' or rec.value_type == 'integer':
                try:
                    value = int(rec.value)
                except ValueError:
                    raise ValidationError(
                        _("Please enter integer value for integer type"))
        return res
