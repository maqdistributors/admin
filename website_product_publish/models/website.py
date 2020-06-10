# coding: utf-8

import logging

from odoo import api, fields, models, tools
from odoo.http import request
from odoo.osv import expression

_logger = logging.getLogger(__name__)


class WebsitePublishedMixin(models.AbstractModel):
    _inherit = 'website.published.mixin'

    published_on_website_ids = fields.Many2many(
        'website', help='Determines on what websites this record will be visible.')


class WebsitePublishedMultiMixin(WebsitePublishedMixin):
    _inherit = 'website.published.multi.mixin'

    website_published = fields.Boolean('Visible on current website',
                                       compute='_compute_website_published',
                                       inverse='_inverse_website_published',
                                       search='_search_website_published')

    @api.multi
    def _compute_website_published(self):
        for record in self:
            current_website_id = self._context.get('website_id')
            if current_website_id:
                record.website_published = current_website_id in record.published_on_website_ids.ids
            else:  # should be in the backend, return things that are published anywhere
                record.website_published = bool(record.published_on_website_ids)

    @api.multi
    def _inverse_website_published(self):
        for record in self:
            current_website_id = self._context.get('website_id')
            if current_website_id:
                current_website = self.env['website'].browse(
                    current_website_id)

                if record.website_published:
                    record.published_on_website_ids |= current_website
                else:
                    record.published_on_website_ids -= current_website

            else:  # this happens when setting e.g. demo data, publish on all
                if record.website_published:
                    record.published_on_website_ids = self.env['website'].search([])
                else:
                    record.published_on_website_ids = False

    def _search_website_published(self, operator, value):
        if not isinstance(value, bool) or operator not in ('=', '!='):
            _logger.warning('unsupported search on website_published: %s, %s', operator, value)
            return [()]

        if operator in expression.NEGATIVE_TERM_OPERATORS:
            value = not value

        current_website_id = self._context.get('website_id')
        if current_website_id:
            return [('published_on_website_ids', 'in' if value is True else 'not in', current_website_id)]
        else:  # should be in the backend, return things that are published anywhere
            return [('published_on_website_ids', '!=' if value is True else '=', False)]

    @api.multi
    def website_publish_button(self):
        if self.env['website'].search_count([]) <= 1:
            return super(WebsitePublishedMixin, self).website_publish_button()
        else:
            # Some models using the mixin put the base url in the
            # website_url (e.g. website_slides' slide.slide), other
            # ones use a relative url (e.g. website_sale's
            # product.template). Since we are going to construct the
            # urls ourselves filter that out.
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            self.website_url = self.website_url.replace(base_url, '')

            wizard = self.env['website.urls.wizard'].create({
                'path': self.website_url,
                'record_id': self.id,
                'model_name': self._name,
            })
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'website.urls.wizard',
                'views': [(False, 'form')],
                'res_id': wizard.id,
                'target': 'new',
            }

    @api.multi
    def toggle_publish(self):
        for record in self:
            record.website_published = not record.website_published
