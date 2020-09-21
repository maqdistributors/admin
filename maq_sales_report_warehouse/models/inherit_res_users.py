# -*- coding: utf-8 -*-

from odoo import models


class ResUser(models.Model):
    _inherit = 'res.users'

    def get_sales_report_ids(self):
        report_ids = []
        company_ids = self.company_ids.ids
        if company_ids:
            if len(company_ids) > 1:
                domain1 = " res_company_id in %s " % (tuple(company_ids),)
                domain2 = " res_company_id not in %s " % (tuple(company_ids),)
            else:
                domain1 = " res_company_id = %s " % company_ids[0]
                domain2 = " res_company_id != %s " % company_ids[0]
            self.env.cr.execute("""
                SELECT DISTINCT sales_report_id
                FROM res_company_sales_report_rel 
                WHERE %s
                AND sales_report_id not in (
                SELECT DISTINCT sales_report_id 
                FROM res_company_sales_report_rel 
                WHERE %s)
                    """%(domain1, domain2))
            report_ids = [x[0] for x in self.env.cr.fetchall()]
        return report_ids
