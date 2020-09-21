# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSale(WebsiteSale):
    """Add partner comment functions to the website_sale controller."""

    @http.route(['/shop/partner_comment'], type='json', auth="public", methods=['POST'], website=True)
    def partner_comment(self, **post):
        """ Json method that used to add a comment when the user enters the comment
            and clicks anywhere outside the input.
        """
        if post.get('comment'):
            order = request.website.sale_get_order()
            redirection = self.checkout_redirection(order)
            if redirection:
                return redirection

            if order and order.id:
                order.write({'partner_comment': post.get('comment')})

        return True

