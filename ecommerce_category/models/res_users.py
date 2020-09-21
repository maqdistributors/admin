# coding: utf-8

import logging

from odoo import api, models, fields, _, SUPERUSER_ID
from odoo.exceptions import AccessDenied
from odoo.http import request

_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = 'res.users'

    login_website_ids = fields.Many2many(comodel_name='website', relation='user_website_login_check',
                                            column1='user_id', column2='website_id', string='Website Allowed Login ',
                                            help='This field must be used for intenral users authetication only and should not be used for portal users.')
    @api.onchange('company_id', 'company_ids')
    def onchange_company(self):
        user_company_websites = self.env['website'].search([('company_id', 'in', self.company_ids.ids)])
        # self.login_website_ids = user_company_websites + self.registered_on_website_id
        self.login_website_ids = user_company_websites


    @classmethod
    def _login(cls, db, login, password):
        """
            override to allow user to login based on their allowed company's website
            for example -
            Maq users should not be able to use their login to login through the joint portal and
            vice versa (joint user should not be able to login to portal using Maq website)
            unless they are a user with access to both companies.

            UPDATE CHANGES ARE MARKED WITH 'CUSTOM'
        """
        #TODO - can we use registered_on_website_id field of res users?
        if not password:
            return False
        user_id = False
        try:
            with cls.pool.cursor() as cr:
                self = api.Environment(cr, SUPERUSER_ID, {})[cls._name]
                user = self.search([('login', '=', login)])
                if user:
                    # START====
                    #TODO: cleanup + better logic
                    current_website_id = self.env['website'].get_current_website()
                    if user.id != SUPERUSER_ID:
                        # Interal user can auth from different website as some company may 
                        # not have website so auth trough website of other company or
                        # allowed login website.
                        # share user auth to their own own website only.
                        if not user.share:
                            user_company_websites = self.env['website'].search([('company_id', 'in', user.company_ids.ids)])
                            auth_allow_website = user.login_website_ids + user_company_websites
                            print (auth_allow_website)
                            if current_website_id not in user.login_website_ids:
                                _logger.info('Multi-website login failed for db:%s login:%s website_id:%s', db, login, current_website_id)
                                user = False
                        elif current_website_id.company_id.id not in user.company_ids.ids:
                            _logger.info('Multi-website company login failed for db:%s login:%s website_id:%s', db, login, current_website_id)
                            user = False
                    #  END====
                    if user and current_website_id:
                        try:
                            user_id = user.id
                            user.sudo(user_id)._check_credentials(password)
                            user.sudo(user_id)._update_last_login()
                        except AccessDenied:
                            _logger.info('Multi-website login failed for db:%s login:%s website_id:%s', db, login, current_website_id)
                            user_id = False
                    else:
                        user_id = False
                else:
                    user_id = False
        except AccessDenied:
            _logger.info('login failed for db:%s login:%s', db, login)
            user_id = False

        if user_id:
            status = "successful"
            ip = request.httprequest.environ['REMOTE_ADDR'] if request else 'n/a'
            _logger.info("Login %s for db:%s login:%s from %s", status, db, login, ip)
            return user_id
        else:
            raise AccessDenied()
