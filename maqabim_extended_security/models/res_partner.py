# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        if self.env.user.has_group('maqabim_extended_security.group_hide_vendors'):
            args.append((('supplier', '=', False)))
        return super(ResPartner, self).search(args, offset=offset, limit=limit, order=order, count=count)
