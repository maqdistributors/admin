# -*- coding: utf-8 -*-

from odoo import api, models, _
from odoo.exceptions import AccessError


class Product(models.Model):
    _inherit = "product.product"

    @api.model
    def create(self, vals):
        if self.env.user.has_group('maqabim_extended_security.group_restrict_product_creation'):
            raise AccessError(_("You are not allowed to create this object. Please contact your system administrator!"))
        return super(Product, self).create(vals)

    @api.multi
    def write(self, vals):
        if self.env.user.has_group('maqabim_extended_security.group_restrict_product_creation'):
            raise AccessError(_("You are not allowed to update this object. Please contact your system administrator!"))
        return super(Product, self).write(vals)

    @api.multi
    def unlink(self):
        if self.env.user.has_group('maqabim_extended_security.group_restrict_product_creation'):
            raise AccessError(_("You are not allowed to delete this object. Please contact your system administrator!"))
        return super(Product, self).unlink()


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.model
    def create(self, vals):
        if self.env.user.has_group('maqabim_extended_security.group_restrict_product_creation'):
            raise AccessError(_("You are not allowed to create this object. Please contact your system administrator!"))
        return super(ProductTemplate, self).create(vals)

    @api.multi
    def write(self, vals):
        if self.env.user.has_group('maqabim_extended_security.group_restrict_product_creation'):
            raise AccessError(_("You are not allowed to update this object. Please contact your system administrator!"))
        return super(ProductTemplate, self).write(vals)

    @api.multi
    def unlink(self):
        if self.env.user.has_group('maqabim_extended_security.group_restrict_product_creation'):
            raise AccessError(_("You are not allowed to delete this object. Please contact your system administrator!"))
        return super(ProductTemplate, self).unlink()
