# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import datetime, date
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from docutils.nodes import reference


class ReturnPicking(models.TransientModel):
    _inherit = 'stock.return.picking'

    @api.model
    def default_get(self, fields):
        """
        1.42 In Customer Shipment, Set the To Refund as Ticked by default in Reverse Transfer screen
        Inherit default_get method and set to_refund boolean as True
        """
        res = super(ReturnPicking, self).default_get(fields)
        return_moves = res.get('product_return_moves')
        ret_move_list = []
        if return_moves:
            for moves in return_moves:
                r_moves = list(moves)
                r_moves[2].update({'to_refund': True})
                moves = tuple(r_moves)
                ret_move_list.append(moves)
            res['product_return_moves'] = ret_move_list
        return res


class Inventory(models.Model):
    _inherit = 'stock.inventory'

    """
    Added new states in state field and new fields
    """
    state = fields.Selection(string='Status', selection=[('draft', 'Draft'), ('cancel', 'Cancelled'), ('confirm', 'In Progress'), ('waiting_approval', 'Waiting for Approval'), ('approved', 'Approved'), ('done', 'Validated')],
                             copy=False, index=True, readonly=True, default='draft')

    approve_id = fields.Many2one("res.partner", "Approved By", readonly=True)
    is_approved = fields.Boolean(default=False, readonly=True)

    m_supplier_ids = fields.Many2many('res.partner', string='Suppliers')
    m_internal_reference = fields.Char(string='Internal Reference')
    m_website_category_ids = fields.Many2many(
        'product.public.category', string='Website Category')
    # 2.00 In Inventory adjustment, Include Exhausted products should be
    # ticked by default
    exhausted = fields.Boolean('Include Exhausted Products', readonly=True, default=True, states={
                               'draft': [('readonly', False)]})
    approve_date = fields.Date(string='Approved Date', readonly=True)
    line_ids = fields.One2many('stock.inventory.line', 'inventory_id', string='Inventories', copy=True, readonly=False, states={
                               'done': [('readonly', True)], 'approved': [('readonly', True)]})

    def action_start(self):
        for inventory in self.filtered(lambda x: x.state not in ('done', 'cancel')):
            vals = {'state': 'confirm', 'date': fields.Datetime.now()}
            if (inventory.filter != 'partial') and not inventory.line_ids:
                vals.update({'line_ids': [
                            (0, 0, line_values) for line_values in inventory._get_inventory_lines_values()]})
            inventory.write(vals)
        return True

    def action_approval(self):
        for inventory in self.filtered(lambda x: x.state not in ('done', 'cancel')):
            vals = {'state': 'waiting_approval', 'date': fields.Datetime.now()}
            if (inventory.filter != 'partial') and not inventory.line_ids:
                vals.update({'line_ids': [
                            (0, 0, line_values) for line_values in inventory._get_inventory_lines_values()]})
            inventory.write(vals)
        return True

    def action_approved(self):
        for inventory in self.filtered(lambda x: x.state not in ('done', 'cancel')):
            vals = {'state': 'approved', 'date': fields.Datetime.now(),
                    'approve_id': self.env.user.partner_id.id,
                    'approve_date': fields.Datetime.now()}
            if (inventory.filter != 'partial') and not inventory.line_ids:
                vals.update({'line_ids': [
                            (0, 0, line_values) for line_values in inventory._get_inventory_lines_values()]})
            inventory.write(vals)
        return True

    def action_cancel_draft(self):
        self.mapped('move_ids')._action_cancel()
        self.write({
            'line_ids': [(5,)],
            'approve_id': None,
            'approve_date': None,
            'state': 'draft'
        })

    def action_cancel_user_draft(self):
        self.mapped('move_ids')._action_cancel()
        self.write({
            'line_ids': [(5,)],
            'state': 'draft'
        })

    @api.model
    def _selection_filter(self):
        """
        Add Custom Selection Options for supplier of product, internal reference, 
        and website catefory of product
        """
        result = super(Inventory, self)._selection_filter()
        result.append(('suppliers', _('Select suppliers')))
        result.append(('reference', _('Product Reference')))
        result.append(('web_categ', _('Website Product Category')))
        return result

    def _get_inventory_lines_values(self):
        """
        Inherit inventory lines method to add inventory line values according to supplier,
        internal reference and website category of the product
        """
        vals = []
        product_obj = self.env['product.product']
        quant_products = self.env['product.product']
        product_supplierinfo_obj = self.env['product.supplierinfo']

        locations = self.env['stock.location'].search(
            [('id', 'child_of', [self.location_id.id])])

        if len(locations.ids) == 1:
            domain = "location_id = %s " % locations.ids[0]
        else:
            domain = "location_id in %s " % (tuple(locations.ids),)

        if self.filter in ('suppliers'):
            product_supplier_ids = product_supplierinfo_obj.search([
                ('name', 'in', self.m_supplier_ids.ids),
            ])
            supplier_ids = []
            for supplier in product_supplier_ids:
                start_date = False
                end_date = False
                if supplier.date_start:
                    start_date = datetime.strptime(
                        supplier.date_start, DEFAULT_SERVER_DATE_FORMAT).date()
                if supplier.date_end:
                    end_date = datetime.strptime(
                        supplier.date_end, DEFAULT_SERVER_DATE_FORMAT).date()
                if start_date and end_date:
                    if (start_date <= datetime.today().date() <= end_date):
                        supplier_ids.append(supplier.id)
                else:
                    supplier_ids.append(supplier.id)
            product_ids = product_obj.search(
                [('seller_ids', 'in', supplier_ids)])
            if len(product_ids.ids) > 1:
                domain += " AND product_id in %s " % (tuple(product_ids.ids),)
            elif len(product_ids.ids) == 1:
                domain += " AND product_id = %s " % product_ids.ids[0]
            qry = """
                SELECT product_id, sum(quantity) as product_qty, location_id
                FROM stock_quant
                WHERE %s
                GROUP BY product_id, location_id""" % (domain)
            self.env.cr.execute(qry)

            for product_data in self.env.cr.dictfetchall():
                for void_field in [item[0] for item in product_data.items() if item[1] is None]:
                    product_data[void_field] = False
                product_data['theoretical_qty'] = product_data['product_qty']
                if product_data['product_id']:
                    product_data['product_uom_id'] = product_obj.browse(
                        product_data['product_id']).uom_id.id
                    quant_products |= product_obj.browse(
                        product_data['product_id'])
                vals.append(product_data)
            if self.exhausted:
                for product in product_ids:
                    product_obj |= product
                exhausted_vals = self._get_exhausted_inventory_line(
                    product_obj, quant_products)
                vals.extend(exhausted_vals)
            return vals
        elif self.filter in ("web_categ"):
            product_website_categ_id = self.env['product.public.category'].search([
                ('id', 'in', self.m_website_category_ids.ids),
            ])
            product_ids = product_obj.search(
                [('public_categ_ids', 'in', product_website_categ_id.ids)])
            if product_ids:
                if len(product_ids.ids) == 1:
                    domain += " AND product_id = %s " % (product_ids.id)
                else:
                    domain += " AND product_id in %s " % (
                        tuple(product_ids.ids),)

                self.env.cr.execute(
                    """SELECT product_id, sum(quantity) as product_qty, location_id
                        FROM stock_quant
                        WHERE %s
                        GROUP BY product_id, location_id""" % (domain))
                for product_data in self.env.cr.dictfetchall():
                    for void_field in [item[0] for item in product_data.items() if item[1] is None]:
                        product_data[void_field] = False
                    product_data['theoretical_qty'] = product_data[
                        'product_qty']
                    if product_data['product_id']:
                        product_data['product_uom_id'] = product_obj.browse(
                            product_data['product_id']).uom_id.id
                        quant_products |= product_obj.browse(
                            product_data['product_id'])
                    vals.append(product_data)
                if self.exhausted:
                    for product in product_ids:
                        product_obj |= product
                    exhausted_vals = self._get_exhausted_inventory_line(
                        product_obj, quant_products)
                    vals.extend(exhausted_vals)
                return vals
            else:
                raise ValidationError(
                    _("Product with the entered category is not available!"))
        elif self.filter in ("reference"):
            internal_ref = self.m_internal_reference
            reference_list = [ref.strip() for ref in internal_ref.split(',')]
            if len(reference_list) == 1:
                product_reference_id = self.env['product.product'].search([
                    ('default_code', 'ilike', reference_list[0]),
                ])
            elif len(reference_list) > 1:
                #                 ref_list = ''
                prod_ref_id = []
                for ref in reference_list:
                    prod_ref_id += self.env['product.product'].search([
                        ('default_code', 'ilike', ref), ]).ids
                product_reference_id = self.env['product.product'].search([
                    ('id', 'in', prod_ref_id),
                ])
#                     ref_list += ref + '|'
#                 ref_list = '%' + ref_list[:-1] + '%'
#                 sql_query = """SELECT id
#                         FROM product_product
#                         WHERE default_code SIMILAR TO '%s';"""%(ref_list)
#                 self.env.cr.execute(sql_query)
#                 results = self.env.cr.fetchall()
#                 result = [res[0] for res in results]
#                 product_reference_id = self.env['product.product'].search([
#                     ('id', 'in', result),
#                 ])
#                 st_line = self.env['account.bank.statement.line']
#             product_reference_id = self.env['product.product'].search([
#                 ('default_code', 'in', reference_list)
#             ])
            product_tuple = ()
            if product_reference_id:
                for reference in product_reference_id:
                    product_tuple = product_tuple + (reference.id,)
                if len(product_tuple) > 1:
                    domain += " AND product_id in %s " % (product_tuple,)
                elif len(product_tuple) == 1:
                    domain += " AND product_id = %s " % product_tuple
                self.env.cr.execute(
                    """SELECT product_id, sum(quantity) as product_qty, location_id
                        FROM stock_quant
                        WHERE %s
                        GROUP BY product_id, location_id""" % (domain))
                for product_data in self.env.cr.dictfetchall():
                    for void_field in [item[0] for item in product_data.items() if item[1] is None]:
                        product_data[void_field] = False
                    product_data['theoretical_qty'] = product_data[
                        'product_qty']
                    if product_data['product_id']:
                        product_data['product_uom_id'] = product_obj.browse(
                            product_data['product_id']).uom_id.id
                        quant_products |= product_obj.browse(
                            product_data['product_id'])
                    vals.append(product_data)
                if self.exhausted:
                    for product in product_reference_id:
                        product_obj |= product
                    exhausted_vals = self._get_exhausted_inventory_line(
                        product_obj, quant_products)
                    vals.extend(exhausted_vals)
                return vals
            else:
                raise ValidationError(_('There are some incorrect Internal reference entered. Please enter exact internal reference!'))
        return super(Inventory, self)._get_inventory_lines_values()
