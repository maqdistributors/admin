# coding: utf-8

import logging

from odoo import api, fields, models, tools, _
from datetime import datetime
from odoo.addons import decimal_precision as dp

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = 'product.template'
    publish_date = fields.Datetime('Publish Date', company_dependent=True)

    @api.multi
    def write(self, vals):
        sale_ok = vals.get('sale_ok')
        if sale_ok == True:
            vals['website_published'] = True
        elif sale_ok is None:
            sale_ok = self.sale_ok
        website_published = vals.get('website_published')
        if website_published == True and sale_ok == True:
            vals['publish_date'] = datetime.now()
        elif website_published == False and sale_ok == True:
            vals['publish_date'] = self.create_date
        elif website_published == False and sale_ok == False:
            vals['publish_date'] = None
        result = super(ProductTemplate, self).write(vals)
        return result
