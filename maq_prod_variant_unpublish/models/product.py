# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ProductProduct(models.Model):

    _inherit = "product.product"

#     @api.onchange("is_website_publish")
#     def onchange_is_website_publish(self):
#         print ("self.is_website_publish --->", self.is_website_publish)
#         if not self.is_website_publish:
#             self.website_ids = None
#         elif self.is_website_publish:
#             current_website_id = self.env['website'].get_current_website()
#             print ("current website id --->>", current_website_id)
#             self.website_ids = current_website_id

#     @api.onchange("is_hide_variant")
#     def onchange_is_variant_hide(self):
#         if self.is_hide_variant == False:
#             self.product_hide_website_ids = None


    is_website_publish = fields.Boolean(
        string="To Show 'Currently Out of Stock' message", company_dependent=True, default=False)
    is_hide_variant = fields.Boolean(
        string='To Hide Product Variant', company_dependent=True, default=False)
#         partners = self.env.user.partner_id
#         active_id = self._context.get('active_id')
#         if self._context.get('active_model') == 'res.partner' and active_id:
#             if active_id not in partners.ids:
#                 partners |= self.env['res.partner'].browse(active_id)
#         return partners

#     website_ids = fields.Many2many("website", relation="product_product_website_rel",
#                                    string="Websites",
#                                    help="IF blank, the product variant will be visible in all websites")

#     product_hide_website_ids = fields.Many2many("website",
#                                                 relation="product_product_hide_website_rel",
#                                                 string="Hide Product from Websites")


#     @api.multi
#     def is_product_variant_publish(self):
#         for rec in self:
#             if rec.website_published:
#                 current_website = rec.env['website'].get_current_website()
#                 if not rec.website_ids and rec.is_website_publish:
#                     return False
#                 elif not rec.is_website_publish and not rec.website_ids:
#                     return True
#                 elif rec.website_ids and rec.is_website_publish:
#                     if current_website.id in rec.website_ids.ids:
#                         return False
#                     else:
#                         return True
#             else:
#                 return False

    @api.multi
    def is_product_variant_publish(self):
        for rec in self:
            if rec.website_published:
                current_company_id = self.env.user.company_id.id
                user_current_website = rec.env['website'].browse(current_company_id)
                current_web = rec.env['website'].get_current_website()
                if rec.is_website_publish and user_current_website.id == current_web.id:
                    return False
                elif not rec.is_website_publish:
                    return True
                else:
                    return True
#                 elif rec.website_ids and rec.is_website_publish:
#                     if current_website.id in rec.website_ids.ids:
#                         return False
#                     else:
#                         return True
            else:
                return False

    @api.multi
    def is_product_variant_hide(self):
        for rec in self:
            if rec.website_published:
                v_current_company_id = self.env.user.company_id.id
                v_user_current_website = rec.env['website'].browse(v_current_company_id)
                v_current_web = rec.env['website'].get_current_website()
                if rec.is_hide_variant and v_user_current_website.id == v_current_web.id:
                    return True
                elif not rec.is_hide_variant:
                    return False
                else:
                    return False
#                 elif rec.product_hide_website_ids and rec.is_hide_variant:
#                     if current_website in rec.product_hide_website_ids:
#                         return True
#                     else:
#                         return False
            else:
                return False


#     @api.onchange('is_website_publish')
#     def _onchange_is_website_publish(self):
#         ''' Onchange method to check for product variant <= 1
#             If the product variant is only 1, then raise message to
#             unpublish product instead of hiding the product on website
#         '''
#         if not self.is_website_publish:
#             product_variant_search_ids = self.search(
#                 [('product_tmpl_id', '=', self.product_tmpl_id.id)])
#             if product_variant_search_ids and len(product_variant_search_ids) <= 1:
#                 warning_mess = {
#                     'title': _('Hide Product on Website Shop!'),
#                     'message': _('You can unpublish the product variant instead of hiding it. There is only one variant for this product ! '),
#                 }
#                 return {'warning': warning_mess}

