# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    m_product_specification_ids = fields.One2many(
        "product.specification.line", "product_tmpl_id", "Product Specifications")

    def _get_published_product_ids(self):
        for rec in self:
            values = []
            for product_variant_id in rec.product_variant_ids:
                if not product_variant_id.is_website_publish:
                    values += [str(product_variant_id.id)]
            return values


# Following specifiaction masters conatins a value to show in website
# specification section
class ProductSpecificationLine(models.Model):
    _name = "product.specification.line"
    _description = "Product Specification"
    _rec_name = 'product_specification_id'

    product_tmpl_id = fields.Many2one(
        'product.template', 'Product Template', ondelete='cascade', required=True)
    product_specification_id = fields.Many2one(
        'product.specification.attribute', 'Attribute', ondelete='restrict', required=True)
    value_ids = fields.Many2many(
        'product.specification.value', string='Attribute Values')

    @api.constrains('value_ids', 'product_specification_id')
    def _check_valid_attribute(self):
        if any(line.value_ids > line.product_specification_id.value_ids for line in self):
            raise ValidationError(
                _('Error ! You cannot use this attribute with the following value.'))
        return True

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        # TDE FIXME: currently overriding the domain; however as it includes a
        # search on a m2o and one on a m2m, probably this will quickly become
        # difficult to compute - check if performance optimization is required
        if name and operator in ('=', 'ilike', '=ilike', 'like', '=like'):
            args = args or []
            domain = ['|', ('product_specification_id', operator,
                            name), ('value_ids', operator, name)]
            return self.search(expression.AND([domain, args]), limit=limit).name_get()
        return super(ProductSpecificationLine, self).name_search(name=name, args=args, operator=operator, limit=limit)


class ProductSpecificationAttribute(models.Model):
    _name = "product.specification.attribute"
    _description = "Product Specification Attribute"
    _order = 'sequence, name'

    name = fields.Char('Name', required=True, translate=True)
    value_ids = fields.One2many(
        'product.specification.value', 'specification_id', 'Values', copy=True)
    sequence = fields.Integer('Sequence', help="Determine the display order")
    attribute_line_ids = fields.One2many(
        'product.specification.line', 'product_specification_id', 'Lines')
    type = fields.Selection(
        [('radio', 'Radio'), ('select', 'Select'), ('color', 'Color')], default='radio')


class ProductSpecificationAttributevalue(models.Model):
    _name = "product.specification.value"
    _description = "Product Specification Value"
    _order = 'sequence, specification_id, id'

    name = fields.Char('Value', required=True, translate=True)
    sequence = fields.Integer('Sequence', help="Determine the display order")
    specification_id = fields.Many2one(
        'product.specification.attribute', 'Specification Attribute', ondelete='cascade', required=True)
    html_color = fields.Char(string='HTML Color Index', oldname='color', help="Here you can set a "
                                                                              "specific HTML color index (e.g. #ff0000) to display the color on the website if the "
                                                                              "attibute type is 'Color'.")
    #     product_ids = fields.Many2many('product.product', string='Variants', readonly=True)
    #     price_extra = fields.Float(
    #         'Attribute Price Extra', compute='_compute_price_extra', inverse='_set_price_extra',
    #         default=0.0, digits=dp.get_precision('Product Price'),
    #         help="Price Extra: Extra price for the variant with this attribute value on sale price. eg. 200 price extra, 1000 + 200 = 1200.")
    #     price_ids = fields.One2many('product.attribute.price', 'value_id', 'Attribute Prices', readonly=True)

    _sql_constraints = [
        ('value_company_uniq', 'unique (name,specification_id)',
         'This attribute value already exists !')
    ]
