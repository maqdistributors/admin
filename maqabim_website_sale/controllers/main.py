from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers import main
from odoo.addons.website_sale.controllers.main import WebsiteSale

main.PPG = 28  # Products Per Page

class MaqabimWebsiteSale(WebsiteSale):

    @http.route()
    def shop(self, page=0, category=None, search='', ppg=False, **post):
        """
            override to block the shop page for non logged user, which is public user.
            click on shop page from public user would redirect to the login page to force
            public user to log in first to play with shoping cart
        """
        # we strictly assume that, they are using group_public as a website user
        if request.env.user.id == request.website.user_id.id:
            url = '/web/login?redirect=/shop'
            if request.env['ir.config_parameter'].sudo().get_param('auth_signup.allow_uninvited') == 'True':
                url = '/web/signup?redirect=/shop'
            return request.redirect(url)
        return super(MaqabimWebsiteSale, self).shop(page=page, category=category, search=search, ppg=ppg, **post)
