import logging
import traceback

from odoo import models, api
from odoo.tools.float_utils import float_compare

_logger = logging.getLogger(__name__)


class ProductPriceHistory(models.Model):
    _inherit = "product.price.history"

    @api.model
    def create(self, vals):
        history = super(ProductPriceHistory, self).create(vals)
        if float_compare(history.cost, 0.00, precision_digits=2) == 0:
            _logger.warning('cost set to 0\n%s', ''.join(traceback.format_stack()))
        return history
