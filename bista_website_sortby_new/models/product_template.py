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
        for rec in self:
            val_sale_ok = vals.get('sale_ok')
            rec_sale_ok = rec.sale_ok
            val_website_published = vals.get('website_published')
            rec_website_published = rec.website_published
            val_publish_date = vals.get('publish_date')
            if val_website_published == True and val_sale_ok == True:
                if val_publish_date:
                    vals['publish_date'] = val_publish_date
                else:
                    vals['publish_date'] = datetime.now()
            elif val_website_published == True and rec_sale_ok == True:
                if val_publish_date:
                    vals['publish_date'] = val_publish_date
                else:
                    vals['publish_date'] = datetime.now()
            elif val_website_published == False and val_sale_ok == True:
                vals['publish_date'] = rec.create_date
            elif rec_website_published == False and val_sale_ok == True:
                vals['publish_date'] = rec.create_date
            elif val_website_published == False and rec_sale_ok == True:
                vals['publish_date'] = rec.create_date
            elif val_website_published == False and val_sale_ok == False:
                vals['publish_date'] = None
            elif rec_website_published == False and val_sale_ok == False:
                vals['publish_date'] = None
            elif val_website_published == False and rec_sale_ok == False:
                vals['publish_date'] = None

        result = super(ProductTemplate, self).write(vals)
        return result
