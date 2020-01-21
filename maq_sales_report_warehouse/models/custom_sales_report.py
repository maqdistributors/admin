# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta, time
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

import logging
_logger = logging.getLogger(__name__)

class SalesReport(models.Model):
    _name = 'sales.report'
    _description = 'Sales Report'
    _inherit = ['mail.thread', 'mail.activity.mixin']


    m_sales_start_date = fields.Datetime(string="Start Date", default=datetime.today().replace(day=1), required=True, track_visibility='onchange')
    m_sales_end_date = fields.Datetime(string="End Date", default=datetime.today(), required=True, track_visibility='onchange')
    m_warehouse_id = fields.Many2many("stock.warehouse", string="Warehouse", required=True, track_visibility='onchange')
    m_exhausted = fields.Boolean("Include Exhausted Products", default=True, track_visibility='onchange')
    m_sales_report_lines = fields.One2many("sales.report.lines", "sales_report_id", "Sales Report Lines", copy=False)
    #TO DO: put domain on partner_ids and show only those vendors who are registred with product.supplierinfo
    company_ids = fields.Many2many("res.company", string="Company", copy=False, track_visibility='onchange')
    product_ids = fields.Many2many("product.product", string="Products in Filter", copy=False, track_visibility='onchange')
    partner_ids = fields.Many2many("res.partner", string="Vendors in Filter", copy=False, track_visibility='onchange')
    internal_ref = fields.Char(string="Internal Reference in Filter", copy=False, track_visibility='onchange')
    prod_ref = fields.Char(string="Product Reference in Filter", copy=False, track_visibility='onchange')
    is_lock = fields.Boolean("Locked", default=False, copy=False, track_visibility='onchange')
    user_id = fields.Many2one('res.users', string='Responsible', required=False, default=lambda self: self.env.user)
    active = fields.Boolean(default=True, copy=False, track_visibility='onchange')
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env['res.company']._company_default_get('sales.report'))
    event_description = fields.Char(string="Event", copy=False, track_visibility='onchange')
    is_update_total_qty = fields.Boolean(default=False, copy=False, track_visibility='onchange')

    @api.model
    def create(self, vals):
        if vals.get('m_warehouse_id'):
            warehouse_id = vals.get('m_warehouse_id')
            warehouse_ids = warehouse_id[0][2]
            company_ids = []
            warehouse_records = self.env['stock.warehouse'].browse(warehouse_ids)
            for warehouse_record in warehouse_records:
                company_id = warehouse_record.company_id
                if company_id:
                    company_ids.append(company_id.id)
            if company_ids:
                vals.update({'company_ids':[[6, 0, list(set(company_ids))]]})
        return super(SalesReport, self).create(vals)

    @api.multi
    def write(self, vals):
        if vals.get('m_warehouse_id'):
            warehouse_id = vals.get('m_warehouse_id')
            warehouse_ids = warehouse_id[0][2]
            company_ids = []
            warehouse_records = self.env['stock.warehouse'].browse(warehouse_ids)
            for warehouse_record in warehouse_records:
                company_id = warehouse_record.company_id
                if company_id:
                    company_ids.append(company_id.id)
            if company_ids:
                vals.update({'company_ids':[[6, 0, list(set(company_ids))]]})
        return super(SalesReport, self).write(vals)

    @api.multi
    def _check_date(self):
        tommorrow_date = datetime.now() + timedelta(days=1)
        tommorrow_min_date = datetime.combine(tommorrow_date, time.min)
        start_date = datetime.strptime(self.m_sales_start_date, DEFAULT_SERVER_DATETIME_FORMAT)
        end_date = datetime.strptime(self.m_sales_end_date, DEFAULT_SERVER_DATETIME_FORMAT)

        if start_date and start_date > tommorrow_min_date:
            raise ValidationError(_("Date should not be future date. Kindly check the start date."))

        if end_date and end_date > tommorrow_min_date:
            raise ValidationError(_("Date should not be future date. Kindly check the end date."))

        if self.m_sales_end_date and self.m_sales_start_date and self.m_sales_end_date < self.m_sales_start_date:
            raise ValidationError(_("End date should be greater than start date"))

    @api.onchange('m_sales_start_date', 'm_sales_end_date')
    def _onchange_date(self):
        self._check_date()

    @api.multi
    def lock_record(self):
        """
        Clear all fields related filters
        """
        self.update({'is_lock':True,
        'event_description':'Lock the record'})

    @api.multi
    def unlock_record(self):
        """
        Clear all fields related filters
        """
        self.update({'is_lock':False,
        'event_description':'Unock the record'})

    @api.multi
    def add_filter(self):
        """
        Show the lines based on filters
        1. Raised warning if values are not set in filters fields
        2. Active all the records if there is any inactive records
        3. prapare domain based on formula
        4. Fetch filter record from domain
        5. Make inactive to rest of the records
        """
        for rec in self:
            if not rec.product_ids and not rec.partner_ids and not rec.internal_ref and not rec.prod_ref:
                raise ValidationError(_("Please add product or vendor details."))
            inactive_records = self.env['sales.report.lines'].sudo().search_count([('active','=',False),
                ('sales_report_id','=',rec.id)])
            if inactive_records > 0:
                self.env.cr.execute("""UPDATE  sales_report_lines
                            SET active = TRUE
                            WHERE sales_report_id = %s"""% rec.id)

            domain = []
            prod_ids = []
            if rec.internal_ref:
                internal_ref = self.internal_ref
                reference_list = [ref.strip() for ref in internal_ref.split(',')]
                if len(reference_list) == 1:
                    prod_ids += self.env['product.product'].search([
                        ('default_code', 'ilike', reference_list[0]),
                    ]).ids
                elif len(reference_list) > 1:
                    for ref in reference_list:
                        prod_ids += self.env['product.product'].search([
                        ('default_code', 'ilike', ref),]).ids
                _logger.info("Len prod_ids in internal_ref************%s"%(len(prod_ids)))
            if rec.prod_ref:
                prod_ref = self.prod_ref
                reference_list = [ref.strip() for ref in prod_ref.split(',')]
                if len(reference_list) == 1:
                    prod_ids += self.env['product.product'].search([
                        ('name', 'ilike', reference_list[0]),
                    ]).ids
                elif len(reference_list) > 1:
                    for ref in reference_list:
                        prod_ids += self.env['product.product'].search([
                        ('name', 'ilike', ref),]).ids
                _logger.info("Len prod_ids in prod_ref************%s"%(len(prod_ids)))
            if rec.product_ids:
                prod_ids += rec.product_ids.ids
                prod_ids = list(set(prod_ids))
                _logger.info("Len prod_ids in product_ids************%s"%(len(prod_ids)))
            if prod_ids:
                domain = [('product_id','in',prod_ids)]
            if rec.partner_ids:
                partner_ids = rec.partner_ids.ids
                if not domain:
                    domain = [('vendor_ids','in',partner_ids)]
                else:
                    if prod_ids:
                        domain = [('product_id','in',prod_ids), ('vendor_ids','in',partner_ids)]
                    else:
                        domain = [('vendor_ids','in',partner_ids)]

            if domain:
                domain += [('sales_report_id','=',rec.id)]
                _logger.info("domain************%s"%(domain))
                records = self.env['sales.report.lines'].sudo().search(domain)
                _logger.info("records************%s"%(records))
                if records:
                    records = records.ids
                    if len(records) > 1:
                        self.env.cr.execute("""UPDATE  sales_report_lines
                                                SET active = FALSE
                                                WHERE id not in %s""",(tuple(records),))
                    else:
                        self.env.cr.execute("""UPDATE  sales_report_lines
                                                SET active = FALSE
                                                WHERE id != %s""" % records[0])
                else:
                    self.env.cr.execute("""UPDATE  sales_report_lines
                                            SET active = FALSE
                                            WHERE sales_report_id = %s"""%rec.id)
        self.update({'event_description':'Clicked on add filter'})


    @api.multi
    def clear_filter(self):
        """
        Clear all fields related filters
        """
        self.update({'product_ids':'', 'partner_ids':'', 'internal_ref':''})
        for rec in self:
            self.env.cr.execute("""UPDATE  sales_report_lines
                            SET active = TRUE
                            WHERE sales_report_id = %s"""% rec.id)
        self.update({'event_description':'Clicked on clear filter'})


    @api.multi
    def clear_data(self):
        """
        Clear all the lines as well as fields related filters
        """
#         self.update({'product_ids':'', 'partner_ids':'', 'internal_ref':''})
        for rec in self:
            self._cr.execute("""DELETE FROM sales_report_lines
                WHERE sales_report_id = %s"""% rec.id)
            #Hide unlink method as it's not delete inactive records
            # if rec.m_sales_report_lines:
                # rec.m_sales_report_lines.unlink()
            # else:
            #     raise ValidationError(_("The Lines are already cleared"))
        self.update({'event_description':'Clicked on clear data'})

    # @api.multi
    # def _get_company_ids(self):
    #     company_ids = []
    #     sw = self.env['stock.warehouse']
    #     for rec in self:
    #         for warehouse_id in rec.m_warehouse_id.ids:
    #             company_id = sw.browse(warehouse_id).company_id.id
    #             if company_id:
    #                 company_ids.append(company_id)
    #     return list(set(company_ids))

    def _get_vendor_details(self, vals):
        vendor_details = ''
        vendors = []

        product_id = self.env['product.product'].browse(vals.get('product_id'))
        if product_id:
            product_tmpl_id = product_id.product_tmpl_id.id
            company_ids = ['',False]
            if vals.get('warehouse_id'):
                c_id = self.env['stock.warehouse'].browse(vals.get('warehouse_id')).company_id
                if c_id:
                    company_ids.append(c_id.id)
            records = self.env['product.supplierinfo'].search([('product_id', '=', product_id.id),('company_id','in',company_ids),
                                                               ('product_tmpl_id', '=', product_tmpl_id)])
            if not records:
                records = self.env['product.supplierinfo'].search(
                    [('product_tmpl_id', '=', product_tmpl_id),('product_id', 'in',['',False]),('company_id','in',company_ids)])

            for record in records:
                try:
                    vendors += [record.name.id]
                    if not vendor_details:
                        vendor_details = record.name.name
                        if record.product_code:
                            vendor_details += ' - ' + record.product_code
                    else:
                        if record.name.name not in vendor_details:
                            vendor_details += ', ' + record.name.name
                            if record.product_code:
                                vendor_details += ' - ' + record.product_code
                except:
                    pass
        return vendors, vendor_details

    def _get_delivered_qty(self, vals):
        """
        Update a delivered qty based on warehouse_id
        """
        for rec in self:
            delivered_qty = 0
            scrap_qty = 0
            return_qty = 0
            if vals.get('warehouse_id') and vals.get('product_id') and vals.get('start_date') and vals.get('end_date'):
                warehouse_id = vals.get('warehouse_id')
                product_id = vals.get('product_id')
                start_date = vals.get('start_date')
                end_date = vals.get('end_date')
                qry = """SELECT pp.id as product_id
                               ,sm.m_warehouse_id as warehouse_id
                               ,SUM(sm.qty_done) as delivered_qty
                        FROM product_product pp
                        LEFT JOIN stock_move_line sm ON (sm.product_id = pp.id)
                        LEFT JOIN stock_location sl ON (sm.location_dest_id = sl.id)
                        WHERE sl.usage in ('customer')
                              AND sm.state = 'done'
                              AND sm.date BETWEEN '%s' and '%s'
                              AND pp.id = %s
                              AND sm.m_warehouse_id = %s
                        GROUP BY 1,2""" % (start_date, end_date, product_id, warehouse_id)
                self.env.cr.execute(qry)
                result = self.env.cr.dictfetchall()

                if result:
                    for res in result:
                        if warehouse_id == res['warehouse_id']:
                            delivered_qty = res['delivered_qty']

                qry = """SELECT pp.id as product_id
                               ,sm.m_warehouse_id as warehouse_id
                               ,SUM(sm.qty_done) as return_qty
                        FROM product_product pp
                        LEFT JOIN stock_move_line sm ON (sm.product_id = pp.id)
                        LEFT JOIN stock_location sl ON (sm.location_id = sl.id)
                        WHERE sl.usage in ('customer')
                              AND sm.state = 'done'
                              AND sm.date BETWEEN '%s' and '%s'
                              AND pp.id = %s
                              AND sm.m_warehouse_id = %s
                        GROUP BY 1,2""" % (start_date, end_date, product_id, warehouse_id)
                self.env.cr.execute(qry)
                result = self.env.cr.dictfetchall()

                if result:
                    for res in result:
                        if warehouse_id == res['warehouse_id']:
                            return_qty = res['return_qty']

                qry = """SELECT pp.id as product_id
                               ,sm.m_warehouse_id as warehouse_id
                               ,SUM(sm.qty_done) as scrap_qty
                        FROM product_product pp
                        LEFT JOIN stock_move_line sm ON (sm.product_id = pp.id)
                        LEFT JOIN stock_location sl ON (sm.location_dest_id = sl.id)
                        WHERE sl.scrap_location = True
                              AND sm.state = 'done'
                              AND sm.date BETWEEN '%s' and '%s'
                              AND pp.id = %s
                              AND sm.m_warehouse_id = %s
                        GROUP BY 1,2""" % (start_date, end_date, product_id, warehouse_id)
                self.env.cr.execute(qry)
                result = self.env.cr.dictfetchall()

                if result:
                    for res in result:
                        if warehouse_id == res['warehouse_id']:
                            scrap_qty = res['scrap_qty']
            return delivered_qty, return_qty, scrap_qty


    def _get_forecasted_qty(self,vals):
        """
        calculate the orecasted qty aginst a warehous and updated in the record
        """
        sml = self.env['stock.move.line']
        for rec in self:
            forecasted_qty = 0
            if vals.get('warehouse_id'):
                domain = ''
                warehouse_rec = warehouse_rec = self.env['stock.warehouse'].browse(vals.get('warehouse_id'))
                warehouse_location_ids = self.env['stock.location'].search([#'|',
                    ('id', 'child_of', warehouse_rec.code),
                    #('usage','in',('customer','supplier'))
                    ]).ids
                if warehouse_location_ids:
                    if len(warehouse_location_ids) > 1:
                        domain = "product_id = "+str(vals.get('product_id'))+" AND location_id in "+str(tuple(warehouse_location_ids))
                    else:
                        domain = "product_id = "+str(vals.get('product_id'))+" AND location_id = "+str((warehouse_location_ids[0]))
                    qr = """
                        SELECT
                            product_id as product_id,
                            sum(product_qty) AS quantity
                        FROM (SELECT
                            MAIN.product_id as product_id,
                            SUM(product_qty) AS product_qty,
                            location_id
                            FROM
                            (SELECT
                                sq.product_id,
                                SUM(sq.quantity) AS product_qty
                                ,location_id.id as location_id
                                FROM
                                stock_quant as sq
                                LEFT JOIN
                                product_product ON product_product.id = sq.product_id
                                LEFT JOIN
                                stock_location location_id ON sq.location_id = location_id.id
                                WHERE
                                location_id.usage = 'internal'
                                GROUP BY sq.product_id,location_id.id
                                UNION ALL
                                SELECT
                                sm.product_id,
                                SUM(sm.product_qty) AS product_qty
                                ,dest_location.id AS location_id
                                FROM
                                   stock_move as sm
                                LEFT JOIN
                                   product_product ON product_product.id = sm.product_id
                                LEFT JOIN
                                stock_location dest_location ON sm.location_dest_id = dest_location.id
                                LEFT JOIN
                                stock_location source_location ON sm.location_id = source_location.id
                                WHERE
                                sm.state IN ('confirmed','partially_available','assigned','waiting') and
                                source_location.usage != 'internal' and dest_location.usage = 'internal'
                                GROUP BY sm.product_id,dest_location.id
                                UNION ALL
                                SELECT
                                sm.product_id,
                                SUM(-(sm.product_qty)) AS product_qty
                                ,source_location.id AS location_id
                                FROM
                                   stock_move as sm
                                LEFT JOIN
                                   product_product ON product_product.id = sm.product_id
                                LEFT JOIN
                                   stock_location source_location ON sm.location_id = source_location.id
                                LEFT JOIN
                                   stock_location dest_location ON sm.location_dest_id = dest_location.id
                                WHERE
                                sm.state IN ('confirmed','partially_available','assigned','waiting') and
                                source_location.usage = 'internal' and dest_location.usage != 'internal'
                                GROUP BY sm.product_id,source_location.id)
                             as MAIN
                        WHERE """+domain+"""
                        GROUP BY MAIN.product_id,location_id
                        ) AS FINAL
                        GROUP BY product_id"""
                    self.env.cr.execute(qr)
                    results = self.env.cr.dictfetchall()
                    for result in results:
                        forecasted_qty = result['quantity']
            return forecasted_qty



    def _get_filter_prod(self,prod_list,company_ids):
        prod_ids = []
        comp_ids = []
        for company_id in company_ids:
            if company_id:
                comp_ids.append(company_id)

        if self.internal_ref:
            internal_ref = self.internal_ref
            reference_list = [ref.strip() for ref in internal_ref.split(',')]
            if len(reference_list) == 1:
                prod_ids += self.env['product.product'].search([('id','in',prod_list),
                    ('default_code', 'ilike', reference_list[0]),
                ]).ids
            elif len(reference_list) > 1:
                for ref in reference_list:
                    prod_ids += self.env['product.product'].search([('id','in',prod_list),
                    ('default_code', 'ilike', ref),]).ids
        if self.prod_ref:
            prod_ref = self.prod_ref
            reference_list = [ref.strip() for ref in prod_ref.split(',')]
            if len(reference_list) == 1:
                prod_ids += self.env['product.product'].search([('id','in',prod_list),
                    ('name', 'ilike', reference_list[0]),
                ]).ids
            elif len(reference_list) > 1:
                for ref in reference_list:
                    prod_ids += self.env['product.product'].search([('id','in',prod_list),
                    ('name', 'ilike', ref),]).ids
        if self.product_ids:
            prod_ids += self.product_ids.ids
        if self.partner_ids:
            prod_data = prod_ids if prod_ids else prod_list
            vendors_ids = self.partner_ids.ids
            records = []

            if len(vendors_ids) == 1:
                domain = "name = %s " % vendors_ids[0]
            else:
                domain = "name in %s " % (tuple(vendors_ids),)

            if len(comp_ids) == 1:
                domain += " AND (company_id = %s or company_id is null)" % comp_ids[0]
            else:
                domain += " AND (company_id in %s or company_id is null) " % (tuple(comp_ids),)

            self.env.cr.execute("""
            SELECT product_tmpl_id
            FROM product_supplierinfo
            WHERE  %s AND product_id is null
            Order BY product_tmpl_id""" % domain)
            tmpl_records = self.env.cr.fetchall()
            _logger.info("tmpl_records----------%s",tmpl_records)
            tmpl_ids = [res[0] for res in tmpl_records]
            if tmpl_ids:
                records += self.env['product.product'].search([('id','in',prod_data),
                    ('product_tmpl_id', 'in', tmpl_ids),]).ids

            if len(prod_data) == 1:
                domain += " AND product_id = %s " % prod_data[0]
            else:
                domain += " AND product_id in %s " % (tuple(prod_data),)

            self.env.cr.execute("""
            SELECT product_id
            FROM product_supplierinfo
            WHERE  %s AND product_id is not null
            Order BY product_tmpl_id""" % domain)
            pro_records = self.env.cr.fetchall()
            pro_records = [res[0] for res in pro_records]
            if pro_records:
                records += pro_records
            prod_ids = list(set(records))
        _logger.info("After filter number of prod_ids***********%s"%len(prod_ids))
        return list(set(prod_ids))
    
    @api.multi
    def generate_report(self):
        """
        Generates report lines
        1. Check the validation base on date and sales report lines
        2. Get all the products associated agianse company id of selected warehouse
        3. gets all the locations from warehouses
        4. based on the locations, gets warehouse base qty on hand aginst product and prepare a vals
        5. Fetch exhausted products
        6. update vals of exhusted product based on warehouse
        7. Create report line using a vals
        """
        _logger.info("Start generate report function")
        # 1. Check the validation base on date and sales report lines
        if self.m_sales_report_lines:
            raise ValidationError(_("Please Clear the Lines data first"))
        self._check_date()


        # 2. Get all the products associated agianse company id of selected warehouse
        # company_ids = self._get_company_ids()
        # company_ids.append(False)
        # prod_list = self.env['product.product'].search([('company_id','in',company_ids),('type', 'not in', ('service', 'consu', 'digital'))]).ids

        # 3. gets all the locations from warehouses
        self.update({'event_description':'Clicked on generate report'})
        for rec in self:
            wr_house_data = []
            start_date = rec.m_sales_start_date
            end_date = rec.m_sales_end_date
            for wr_house in rec.m_warehouse_id:
                location_list = []
                locations = []
                flat_list_locations = []
                company_ids = [wr_house.company_id.id] if wr_house.company_id else []
                company_ids.append(False)
                prod_list = self.env['product.product'].sudo().search([('company_id','in',company_ids),('type', 'not in', ('service', 'consu', 'digital'))]).ids
                _logger.info("Number of product ids associated with warehouse %s******************%s"%(wr_house.name,len(prod_list)))
                if rec.internal_ref or rec.prod_ref or rec.product_ids or rec.partner_ids:
                    prod_list = rec._get_filter_prod(prod_list,company_ids)
                    if not prod_list:
                        continue
                # prod_list = [46106]
                warehouse_location_id = self.env['stock.location'].search([('m_warehouse_id', '=', wr_house.id)])
                if not warehouse_location_id:
                    warehouse_location_id = wr_house.company_id.shopify_location_id
                if len(warehouse_location_id) >= 1:
                    location_list.append(warehouse_location_id)
                    for loc in location_list:
                        locations.append(loc.ids)
                    for locat in locations:
                        for l in locat:
                            flat_list_locations.append(l)
    #                 tuple_locations = tuple(flat_list_locations)
    #                 domain = ' sq.location_id in %s AND sq.product_id in %s'
    #                 args = (tuple_locations,tuple(prod_list))
                    if len(flat_list_locations) == 1:
                        domain = "sq.location_id = %s " % flat_list_locations[0]
                    else:
                        domain = "sq.location_id in %s " % (tuple(flat_list_locations),)

                    if len(prod_list) == 1:
                        domain += " AND sq.product_id = %s " % prod_list[0]
                    else:
                        domain += " AND sq.product_id in %s " % (tuple(prod_list),)

                    # 4. based on the locations, gets warehouse base qty on hand aginst product and prepare a vals
                    vals = []
                    Product = self.env['product.product']
                    # # Empty recordset of products available in stock_quants
                    quant_products = self.env['product.product']
                    # # Empty recordset of products to filter
                    products_to_filter = self.env['product.product'].browse(prod_list)

                    self.env.cr.execute("""
                        SELECT product_id, qty_on_hand, warehouse_id
                        FROM
                        (
                            SELECT sq.product_id as product_id, sum(sq.quantity) as qty_on_hand, sl.m_warehouse_id as warehouse_id
                            FROM stock_quant sq
                            LEFT JOIN product_product pp ON pp.id = sq.product_id
                            LEFT JOIN stock_location sl ON sl.id = sq.location_id
                            WHERE %s -- AND sq.product_id = 51530
                            GROUP BY product_id, sl.m_warehouse_id
                        ) t
                        WHERE t.warehouse_id is not null
                        """ % domain)
                    results = self.env.cr.dictfetchall()
                    _logger.info("stock quants records ------%s"%len(results))
                    if results:
                        wr_house_data.extend(results)

                    for product_data in results:
                        if product_data['product_id']:
                            quant_products |= Product.browse(product_data['product_id'])

                    # 5. Fetch exhausted products
                    if self.m_exhausted:
                        _logger.info("Start with exhausted values fetch")
                        exhausted_vals = self._get_exhausted_inventory_line(products_to_filter, quant_products)
                        exhausted_values = []
                        # 6. update vals of exhusted product based on warehouse
                        for exhausted_val in exhausted_vals:
                            # for warehouse_id in self.m_warehouse_id.ids:
                            temp_val = {}
                            temp_val.update(exhausted_val)
                            temp_val.update({'warehouse_id':wr_house.id,'qty_on_hand':0})
                            exhausted_values.extend([temp_val])
                        if exhausted_values:
                            wr_house_data.extend(exhausted_values)
                        _logger.info("End with exhausted values fetch")
                else:
                    raise ValidationError(_("Location is not set against '%s' warehouse")%wr_house.name)

            # if wr_house_data:
            #     values = []
            #     date_vals = {'start_date':rec.m_sales_start_date, 'end_date':rec.m_sales_end_date}
            #     for line_values in wr_house_data:
            #         line_values.update(date_vals)
            #         values.append((0, False, line_values))
            #     print("Lenghth of data *********---->",len(values))
            #     rec.update({'m_sales_report_lines': values})
            if wr_house_data:
                values = []
                _logger.info("Start updating delivered qty and forecasted qty")
                for line_values in wr_house_data:
#                     _logger.info("Start Calculating vendor_details")
                    line_values.update({'start_date':start_date,'end_date':end_date})
                    vendors, vendor_details = self._get_vendor_details(line_values)
                    if vendors or vendor_details:
                        line_values.update({
                            'vendor_details':vendor_details,
                            'vendor_ids':[[6, False, vendors]],
                            })
#                     _logger.info("End Calculating vendor_details")
#                     _logger.info("Start Calculating  product fields")
                    if line_values.get('product_id'):
                        prod_rec = self.env['product.product'].browse(line_values.get('product_id'))
                        default_code = prod_rec.default_code or ''
                        sales_price = prod_rec.lst_price or ''
                        line_values.update({'default_code':default_code,'sales_price':sales_price})
#                     _logger.info("End Calculating product fields")

#                     _logger.info("Start Calculating delivered_qty")
#                     delivered_qty = self._get_delivered_qty(line_values)
                    delivered_qty, return_qty, scrap_qty = self._get_delivered_qty(line_values)
                    actual_delivered_qty = delivered_qty + scrap_qty - return_qty
                    line_values.update({'delivered_qty':delivered_qty,
                                        'return_qty':return_qty, 'scrap_qty':scrap_qty,
                                        'actual_delivered_qty':actual_delivered_qty})
#                     _logger.info("End Calculating delivered_qty")

#                     _logger.info("Start Calculating forecasted_qty")
                    forecasted_qty = self._get_forecasted_qty(line_values)
                    line_values.update({'forecasted_qty':forecasted_qty})
#                     _logger.info("End Calculating forecasted_qty")
                    values.append((0, False, line_values))
                _logger.info("End with updating delivered qty and forecasted qty")

                if values:
                    _logger.info("Start creating sales report lines")
                    rec.update({'m_sales_report_lines':values})
                    _logger.info("sales report lines created sucessfully")
            if rec.is_update_total_qty:
                query = """
                    UPDATE sales_report_lines srl
                    SET total_qty_on_hand = (SELECT SUM(qty_on_hand)
                                            FROM sales_report_lines
                                            WHERE sales_report_id = '"""+str(rec.id)+"""'
                                            AND product_id = srl.product_id)
                    , total_delivered_qty = (SELECT SUM(actual_delivered_qty)
                                            FROM sales_report_lines
                                            WHERE sales_report_id = '"""+str(rec.id)+"""'
                                            AND product_id = srl.product_id)
                    , total_forecasted_qty = (SELECT SUM(forecasted_qty)
                                            FROM sales_report_lines
                                            WHERE sales_report_id = '"""+str(rec.id)+"""'
                                            AND product_id = srl.product_id)
                    WHERE sales_report_id = '"""+str(rec.id)+"'";
                results = self.env.cr.execute(query)
        _logger.info("End generate report function")

#     @api.multi
#     def generate_report(self):
#         """
#         Generates report lines
#         1. Check the validation base on date and sales report lines
#         2. Get all the products associated agianse company id of selected warehouse
#         3. gets all the locations from warehouses
#         4. based on the locations, gets warehouse base qty on hand aginst product and prepare a vals
#         5. Fetch exhausted products
#         6. update vals of exhusted product based on warehouse
#         7. Create report line using a vals
#         """
#         # 1. Check the validation base on date and sales report lines
#         if self.m_sales_report_lines:
#             raise ValidationError(_("Please Clear the Lines data first"))
#         self._check_date()

#         location_list = []
#         locations = []
#         flat_list_locations = []
#         company_ids = []

#         # 2. Get all the products associated agianse company id of selected warehouse
#         company_ids = self._get_company_ids()
#         company_ids.append(False)
#         prod_list = self.env['product.product'].search([('company_id','in',company_ids),('type', 'not in', ('service', 'consu', 'digital'))]).ids

#         # 3. gets all the locations from warehouses
#         for rec in self:
#             for wr_house in rec.m_warehouse_id:
# #                     warehouse_location_id = self.env['stock.location'].search([('id', 'child_of', wr_house.code), ('usage', '=', 'internal')])
#                 warehouse_location_id = self.env['stock.location'].search([('m_warehouse_id', '=', wr_house.id)])
#                 location_list.append(warehouse_location_id)
#         for loc in location_list:
#             locations.append(loc.ids)
#         for locat in locations:
#             for l in locat:
#                 flat_list_locations.append(l)
#         tuple_locations = tuple(flat_list_locations)
#         domain = ' sq.location_id in %s AND sq.product_id in %s'
#         args = (tuple_locations,tuple(prod_list))

#         # 4. based on the locations, gets warehouse base qty on hand aginst product and prepare a vals
#         vals = []
#         Product = self.env['product.product']
#         # # Empty recordset of products available in stock_quants
#         quant_products = self.env['product.product']
#         # # Empty recordset of products to filter
#         products_to_filter = self.env['product.product'].browse(prod_list)

#         self.env.cr.execute("""
#             SELECT product_id, qty_on_hand, warehouse_id
#             FROM
#             (
#                 SELECT sq.product_id as product_id, sum(sq.quantity) as qty_on_hand, sl.m_warehouse_id as warehouse_id
#                 FROM stock_quant sq
#                 LEFT JOIN product_product pp ON pp.id = sq.product_id
#                 LEFT JOIN stock_location sl ON sl.id = sq.location_id
#                 WHERE %s -- AND product_id = 32
#                 GROUP BY product_id, sl.m_warehouse_id
#             ) t
#             WHERE t.warehouse_id is not null
#             """ % domain, args)
#         results = self.env.cr.dictfetchall()

#         for product_data in results:
#             if product_data['product_id']:
#                 quant_products |= Product.browse(product_data['product_id'])

#         # 5. Fetch exhausted products
#         if self.m_exhausted:
#             exhausted_vals = self._get_exhausted_inventory_line(products_to_filter, quant_products)
#             exhausted_values = []
#             # 6. update vals of exhusted product based on warehouse
#             for exhausted_val in exhausted_vals:
#                 for warehouse_id in self.m_warehouse_id.ids:
#                     temp_val = {}
#                     temp_val.update(exhausted_val)
#                     temp_val.update({'warehouse_id':warehouse_id,'qty_on_hand':0})
#                     exhausted_values.extend([temp_val])
#             results.extend(exhausted_values)

#         # 7. Create report line using a vals
#         values = {}
#         for prod_line in self:
#             values.update({'m_sales_report_lines': [(0, False, line_values) for line_values in results]})
#             prod_line.write(values)
#         ####
#         # mcompany_id = []
#         # for sales_report_line in self.m_sales_report_lines:
#         #     if sales_report_line.company_id.id not in mcompany_id:
#         #         mcompany_id.append(sales_report_line.company_id.id)
#         # else:
#         #     raise ValidationError(_("Please Clear the Lines data first"))

    def _get_exhausted_inventory_line(self, products, quant_products):
        '''
        This function return inventory lines for exausted products
        :param products: products With Selected Filter.
        :param quant_products: products available in stock_quants
        '''
        vals = []
        exhausted_domain = [('type', 'not in', ('service', 'consu', 'digital'))]
        if products:
            exhausted_products = products - quant_products
            exhausted_domain += [('id', 'in', exhausted_products.ids)]
        else:
            exhausted_domain += [('id', 'not in', quant_products.ids)]
        exhausted_products = self.env['product.product'].search(exhausted_domain)

        for product in exhausted_products:
            vals.append({'product_id': product.id,})
        # return [{'product_id': 46106}]
        return vals


class SalesReportLines(models.Model):
    _name = 'sales.report.lines'
    _description = 'Sales Report Lines'
    _order = 'product_id, warehouse_id'

    sales_report_id = fields.Many2one("sales.report", string="Sales Report")
    product_id = fields.Many2one("product.product", string="Product")
    default_code = fields.Char(string="Internal Reference")
#     company_id = fields.Many2one(related='product_id.company_id', string="Product Company")
#     sales_price = fields.Float(related='product_id.lst_price', string="Sale Price")
    sales_price = fields.Float(string="Sale Price")
#     delivered_qty = fields.Float(string="Delivered Quantity", compute="_get_delivered_qty")
    delivered_qty = fields.Float(string="Delivered Quantity")
    scrap_qty = fields.Float(string="Scrap Quantity")
    return_qty = fields.Float(string="Return Quantity")
    actual_delivered_qty = fields.Float(string="Actual Delivered Quantity")
    total_delivered_qty = fields.Float(string="Total Delivered Quantity")
    qty_on_hand = fields.Float(string="Quantity on Hand")
    total_qty_on_hand = fields.Float(string="Total Quantity on Hand")
#     forecasted_qty = fields.Float(string="Forecasted Quantity", compute="_compute_forecasted_qty")
    forecasted_qty = fields.Float(string="Forecasted Quantity")
    total_forecasted_qty = fields.Float(string="Total Forecasted Quantity")
    warehouse_id = fields.Many2one("stock.warehouse", string="Warehouse")
    vendor_ids = fields.Many2many('res.partner', string="Vendors")
    vendor_details = fields.Char(string="Vendors Details")
    start_date = fields.Datetime(string="Start Date")
    end_date = fields.Datetime(string="End Date")
#     m_sales_start_date = fields.Datetime(related='sales_report_id.m_sales_start_date', string="Start Date")
#     m_sales_end_date = fields.Datetime(related='sales_report_id.m_sales_end_date', string="End Date")
    active = fields.Boolean("Active", default=True)


    # @api.model
    # def create(self, vals):
    #     """
    #     While creating a record fetch vendor ids and code from product supplier info
    #     and update it against the record
    #     """
    #     vendor_details, vendors, default_code = self._get_vendor_details(vals)
    #     if vendor_details:
    #         vals.update({'vendor_details':vendor_details})
    #     if vendors:
    #         vals.update({'vendor_ids':[[6, False, vendors]]})

    #     if default_code:
    #         vals.update({'default_code':default_code})

    #     delivered_qty = self._get_delivered_qty(vals)
    #     vals.update({'delivered_qty':delivered_qty})
    #     forecasted_qty = self._get_forecasted_qty(vals)
    #     vals.update({'forecasted_qty':forecasted_qty})
    #     return super(SalesReportLines, self).create(vals)

    # def _get_vendor_details(self, vals):
    #     vendor_details = ''
    #     vendors = []
    #     default_code = ''
    #     if vals.get('product_id'):
    #         #Prepare a vals for vendor details
    #         product_id = self.env['product.product'].browse(vals.get('product_id'))

    #         default_code = product_id.default_code

    #         product_tmpl_id = product_id.product_tmpl_id.id
    #         records = self.env['product.supplierinfo'].search([('product_id', '=', product_id.id),
    #                                                            ('product_tmpl_id', '=', product_tmpl_id)])
    #         if not records:
    #             records = self.env['product.supplierinfo'].search(
    #                 [('product_tmpl_id', '=', product_tmpl_id)])

    #         for record in records:
    #             try:
    #                 vendors += [record.name.id]
    #                 if not vendor_details:
    #                     vendor_details = record.name.name
    #                     if record.product_code:
    #                         vendor_details += ' - ' + record.product_code
    #                 else:
    #                     if record.name.name not in vendor_details:
    #                         vendor_details += ', ' + record.name.name
    #                         if record.product_code:
    #                             vendor_details += ' - ' + record.product_code
    #             except:
    #                 pass
    #     return vendor_details, vendors, default_code

    # def _get_delivered_qty(self,vals):
    #     """
    #     Update a delivered qty based on warehouse_id
    #     """
    #     delivered_qty = 0
    #     warehouse = vals.get('warehouse_id')
    #     product_id = vals.get('product_id')
    #     start_date = vals.get('start_date')
    #     end_date = vals.get('end_date')
    #     qry = """SELECT pp.id as product_id
    #                    ,sm.m_warehouse_id as warehouse_id
    #                    ,SUM(sm.qty_done) as delivered_qty
    #             FROM product_product pp
    #             LEFT JOIN stock_move_line sm ON (sm.product_id = pp.id)
    #             LEFT JOIN stock_location sl ON (sm.location_dest_id = sl.id)
    #             WHERE sl.usage in ('customer')
    #                   AND sm.state = 'done'
    #                   AND sm.date BETWEEN '%s' and '%s'
    #                  AND pp.id = %s
    #                  AND sm.m_warehouse_id = %s
    #             GROUP BY 1,2""" % (start_date, end_date, product_id,warehouse)
    #     self.env.cr.execute(qry)
    #     result = self.env.cr.dictfetchall()
    #     if result:
    #         for res in result:
    #             if warehouse == res['warehouse_id']:
    #                 delivered_qty = res['delivered_qty']
    #     return delivered_qty


    # def _get_forecasted_qty(self,vals):
    #     """
    #     calculate the orecasted qty aginst a warehous and updated in the record
    #     """
    #     domain = ''
    #     forecasted_qty = 0
    #     warehouse = vals.get('warehouse_id')
    #     product_id = vals.get('product_id')
    #     start_date = vals.get('start_date')
    #     end_date = vals.get('end_date')
    #     warehouse_rec = self.env['stock.warehouse'].browse(warehouse)
    #     warehouse_location_ids = self.env['stock.location'].search([('id', 'child_of', warehouse_rec.code)]).ids
    #     if warehouse_location_ids:
    #         if len(warehouse_location_ids) > 1:
    #             domain = "product_id = "+str(product_id)+" AND location_id in "+str(tuple(warehouse_location_ids))
    #         else:
    #             domain = "product_id = "+str(product_id)+" AND location_id = "+str((warehouse_location_ids[0]))
    #         qr = """
    #             SELECT
    #                 product_id as product_id,
    #                 sum(product_qty) AS quantity
    #             FROM (SELECT
    #                 MAIN.product_id as product_id,
    #                 SUM(product_qty) AS product_qty,
    #                 location_id
    #                 FROM
    #                 (SELECT
    #                     sq.product_id,
    #                     SUM(sq.quantity) AS product_qty
    #                     ,location_id.id as location_id
    #                     FROM
    #                     stock_quant as sq
    #                     LEFT JOIN
    #                     product_product ON product_product.id = sq.product_id
    #                     LEFT JOIN
    #                     stock_location location_id ON sq.location_id = location_id.id
    #                     WHERE
    #                     location_id.usage = 'internal'
    #                     GROUP BY sq.product_id,location_id.id
    #                     UNION ALL
    #                     SELECT
    #                     sm.product_id,
    #                     SUM(sm.product_qty) AS product_qty
    #                     ,dest_location.id AS location_id
    #                     FROM
    #                        stock_move as sm
    #                     LEFT JOIN
    #                        product_product ON product_product.id = sm.product_id
    #                     LEFT JOIN
    #                     stock_location dest_location ON sm.location_dest_id = dest_location.id
    #                     LEFT JOIN
    #                     stock_location source_location ON sm.location_id = source_location.id
    #                     WHERE
    #                     sm.state IN ('confirmed','partially_available','assigned','waiting') and
    #                     source_location.usage != 'internal' and dest_location.usage = 'internal'
    #                     GROUP BY sm.product_id,dest_location.id
    #                     UNION ALL
    #                     SELECT
    #                     sm.product_id,
    #                     SUM(-(sm.product_qty)) AS product_qty
    #                     ,source_location.id AS location_id
    #                     FROM
    #                        stock_move as sm
    #                     LEFT JOIN
    #                        product_product ON product_product.id = sm.product_id
    #                     LEFT JOIN
    #                        stock_location source_location ON sm.location_id = source_location.id
    #                     LEFT JOIN
    #                        stock_location dest_location ON sm.location_dest_id = dest_location.id
    #                     WHERE
    #                     sm.state IN ('confirmed','partially_available','assigned','waiting') and
    #                     source_location.usage = 'internal' and dest_location.usage != 'internal'
    #                     GROUP BY sm.product_id,source_location.id)
    #                  as MAIN
    #             WHERE """+domain+"""
    #             GROUP BY MAIN.product_id,location_id
    #             ) AS FINAL
    #             GROUP BY product_id"""
    #         self.env.cr.execute(qr)
    #         results = self.env.cr.dictfetchall()
    #         for result in results:
    #             forecasted_qty = result['quantity']
    #     return forecasted_qty

#     @api.multi
#     @api.depends("product_id", "m_sales_start_date", "m_sales_end_date")
#     def _get_delivered_qty(self):
#         """
#         Update a delivered qty based on warehouse_id
#         """
#         for rec in self:
#             warehouse = rec.warehouse_id
#             qry = """SELECT pp.id as product_id
#                            ,sm.m_warehouse_id as warehouse_id
#                            ,SUM(sm.qty_done) as delivered_qty
#                     FROM product_product pp
#                     LEFT JOIN stock_move_line sm ON (sm.product_id = pp.id)
#                     LEFT JOIN stock_location sl ON (sm.location_dest_id = sl.id)
#                     WHERE sl.usage in ('customer')
#                           AND sm.state = 'done'
#                           AND sm.date BETWEEN '%s' and '%s'
#                          AND pp.id = %s
#                     GROUP BY 1,2""" % (rec.m_sales_start_date, rec.m_sales_end_date, rec.product_id.id)
#             self.env.cr.execute(qry)
#             result = self.env.cr.dictfetchall()
#             if result:
#                 for res in result:
#                     if warehouse.id == res['warehouse_id']:
#                         rec.delivered_qty = res['delivered_qty']
#                     # elif not warehouse:
#                     #     rec.warehouse_id = res['warehouse_id']
#                     #     rec.delivered_qty += res['delivered_qty']
#             else:
#                 rec.delivered_qty = 0

#     @api.multi
#     @api.depends("product_id", "qty_on_hand", "m_sales_start_date", "m_sales_end_date")
#     def _compute_forecasted_qty(self):
#         """
#         calculate the orecasted qty aginst a warehous and updated in the record
#         """
#         sml = self.env['stock.move.line']
#         for rec in self:
#             domain = ''
#             warehouse_id = rec.warehouse_id
#             warehouse_location_ids = self.env['stock.location'].search([#'|',
#                 ('id', 'child_of', warehouse_id.code),
#                 #('usage','in',('customer','supplier'))
#                 ]).ids
#             if warehouse_location_ids:
#                 if len(warehouse_location_ids) > 1:
#                     domain = "product_id = "+str(rec.product_id.id)+" AND location_id in "+str(tuple(warehouse_location_ids))
#                 else:
#                     domain = "product_id = "+str(rec.product_id.id)+" AND location_id = "+str((warehouse_location_ids[0]))
#                 qr = """
#                     SELECT
#                         product_id as product_id,
#                         sum(product_qty) AS quantity
#                     FROM (SELECT
#                         MAIN.product_id as product_id,
#                         SUM(product_qty) AS product_qty,
#                         location_id
#                         FROM
#                         (SELECT
#                             sq.product_id,
#                             SUM(sq.quantity) AS product_qty
#                             ,location_id.id as location_id
#                             FROM
#                             stock_quant as sq
#                             LEFT JOIN
#                             product_product ON product_product.id = sq.product_id
#                             LEFT JOIN
#                             stock_location location_id ON sq.location_id = location_id.id
#                             WHERE
#                             location_id.usage = 'internal'
#                             GROUP BY sq.product_id,location_id.id
#                             UNION ALL
#                             SELECT
#                             sm.product_id,
#                             SUM(sm.product_qty) AS product_qty
#                             ,dest_location.id AS location_id
#                             FROM
#                                stock_move as sm
#                             LEFT JOIN
#                                product_product ON product_product.id = sm.product_id
#                             LEFT JOIN
#                             stock_location dest_location ON sm.location_dest_id = dest_location.id
#                             LEFT JOIN
#                             stock_location source_location ON sm.location_id = source_location.id
#                             WHERE
#                             sm.state IN ('confirmed','partially_available','assigned','waiting') and
#                             source_location.usage != 'internal' and dest_location.usage = 'internal'
#                             GROUP BY sm.product_id,dest_location.id
#                             UNION ALL
#                             SELECT
#                             sm.product_id,
#                             SUM(-(sm.product_qty)) AS product_qty
#                             ,source_location.id AS location_id
#                             FROM
#                                stock_move as sm
#                             LEFT JOIN
#                                product_product ON product_product.id = sm.product_id
#                             LEFT JOIN
#                                stock_location source_location ON sm.location_id = source_location.id
#                             LEFT JOIN
#                                stock_location dest_location ON sm.location_dest_id = dest_location.id
#                             WHERE
#                             sm.state IN ('confirmed','partially_available','assigned','waiting') and
#                             source_location.usage = 'internal' and dest_location.usage != 'internal'
#                             GROUP BY sm.product_id,source_location.id)
#                          as MAIN
#                     WHERE """+domain+"""
#                     GROUP BY MAIN.product_id,location_id
#                     ) AS FINAL
#                     GROUP BY product_id"""
#                 self.env.cr.execute(qr)
#                 results = self.env.cr.dictfetchall()
#                 for result in results:
#                     rec.forecasted_qty = result['quantity']
#             else:
#                 rec.forecasted_qty = 0


    # @api.multi
    # @api.depends("delivered_qty","qty_on_hand","forecasted_qty")
    # def _compute_total(self):
    #     """
    #     Update Total qty group by on product_id
    #     """
    #     _logger.info("Start _compute_total function")
    #     for rec in self:
    #         sales_report_id = rec.sales_report_id.id
    #         product_id = rec.product_id.id
    #         records = self.search([('product_id','=',product_id),('sales_report_id','=',sales_report_id)])
    #         total_delivered_qty = 0
    #         total_qty_on_hand = 0
    #         total_forecasted_qty = 0
    #         for record in records:
    #             total_delivered_qty += record.delivered_qty
    #             total_qty_on_hand += record.qty_on_hand
    #             total_forecasted_qty += record.forecasted_qty
    #         rec.update({'total_delivered_qty':total_delivered_qty,
    #             'total_qty_on_hand':total_qty_on_hand,
    #             'total_forecasted_qty':total_forecasted_qty})
    #     _logger.info("End _compute_total function")
