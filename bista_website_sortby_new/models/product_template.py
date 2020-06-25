# coding: utf-8

import logging

from odoo import api, fields, models, tools, _
from datetime import datetime
from odoo.addons import decimal_precision as dp
# from odoo.exceptions import UserError, ValidationError
# from datetime import datetime

_logger = logging.getLogger(__name__)

class ProductTemplate(models.Model):
    _inherit='product.template'

    publish_date = fields.Datetime('Publish Date', company_dependent=True)

    @api.multi
    def write(self, vals):

        if vals.get('website_published') == True:
            vals['publish_date'] = datetime.now()
        elif vals.get('website_published') == False:
            vals['publish_date'] = self.create_date

        result = super(ProductTemplate, self).write(vals)

        return result


