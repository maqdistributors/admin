# Copyright 2016 Stanislav Krotov <https://it-projects.info/team/ufaks>
# Copyright 2016 manawi <https://github.com/manawi>
# Copyright 2019 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
# License MIT (https://opensource.org/licenses/MIT).

from odoo import api, fields, models


class PosConfig(models.Model):
    _inherit = "pos.config"

    @api.model
    def _default_negative_stock_user(self):
        return self.env.ref("point_of_sale.group_pos_manager")

    negative_order_warning = fields.Boolean(
        "Show Warning",
        help="Show Warning on adding out of stock products",
        default=False,
    )
