# -*- coding: utf-8 -*-
from odoo import models, fields, api


class WebsitePublishedWizard(models.TransientModel):
    _inherit = 'website.urls.wizard'
    ''' Updated the create function to display the website according to allowed companies of user'''
    @api.model
    def create(self, vals):
        res = super(WebsitePublishedWizard, self).create(vals)
        res.update({'website_urls':[(5,)]})
        for website in self.env['website'].search([('company_id','=',self.env.user.company_id.id)]):
            self.env['website.url'].create({
                'wizard_id': res.id,
                'url': 'http://%s%s' % (website.domain, res.path if res.path != '#' else ''),
                'display_goto': res.path != '#',
                'website_id': website.id,
                'record_id': res.record_id,
                'model_name': res.model_name,
            })
        return res

class WebsitePublishedMixin(models.AbstractModel):
    _inherit = 'website.published.multi.mixin'

    @api.multi
    def _compute_website_published(self):
        for record in self:
            current_website_id = self._context.get('website_id')
            current_company_id = self.env.user.company_id
            if current_company_id:
                current_company_id = current_company_id.id
                current_website_rec = record.env['website'].search([('company_id','=',current_company_id)],limit=1)
                if current_website_rec:
                    current_website_id = current_website_rec.id
            if current_website_id:
                record.website_published = current_website_id in record.published_on_website_ids.ids
            else:  # should be in the backend, return things that are published anywhere
                record.website_published = False
