# coding: utf-8

import logging

from odoo import api, fields, models


class WebsiteURL(models.TransientModel):
    _name = 'website.url'

    url = fields.Char(readonly=True)
    wizard_id = fields.Many2one(
        'website.urls.wizard', ondelete='cascade', readonly=True)

    record_id = fields.Integer(required=True, readonly=True)
    model_name = fields.Char(required=True, readonly=True)
    website_id = fields.Many2one('website', required=True, readonly=True)
    display_goto = fields.Boolean(required=True, readonly=True)

    published = fields.Boolean(compute='_compute_published')

    @api.multi
    def _compute_published(self):
        for url in self:
            url.published = url._get_record().website_published

    @api.multi
    def action_goto(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': self.url,
            'target': 'self',
        }

    @api.multi
    def action_publish(self):
        self.ensure_one()
        self._get_record().toggle_publish()

        # todo jov this prevents closing of the popup, I remember
        # there being a better way to do this...
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'website.urls.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': self.wizard_id.id,
        }

    def _get_record(self):
        self.ensure_one()
        return self.env[self.model_name].browse(self.record_id).with_context(website_id=self.website_id.id)


class WebsitePublishedWizard(models.TransientModel):
    _name = 'website.urls.wizard'

    path = fields.Char(readonly=True)
    record_id = fields.Integer(required=True, readonly=True)
    model_name = fields.Char(required=True, readonly=True)
    website_urls = fields.One2many('website.url', 'wizard_id')

    @api.model
    def create(self, vals):
        res = super(WebsitePublishedWizard, self).create(vals)

        for website in self.env['website'].search([('company_id','=', self.env.user.company_id.id)]):
            # todo jov fix port somehow
            self.env['website.url'].create({
                'wizard_id': res.id,
                'url': 'http://%s%s' % (website.domain, res.path if res.path != '#' else ''),
                'display_goto': res.path != '#',
                'website_id': website.id,
                'record_id': res.record_id,
                'model_name': res.model_name,
            })

        return res
