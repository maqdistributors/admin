

from odoo import models, fields, api, _
from odoo.osv import expression


class PosCategory(models.Model):

	_inherit = 'pos.category'

	@api.model
	def name_search(self, name='', args=None, operator='ilike', limit=100):
		if operator in ('ilike','like','=','=like','=ilike'):
			domain = expression.AND([
				args or [],
				['|', '|', '|', ('name', operator, name), ('parent_id.name', operator, name), ('parent_id.parent_id.name', operator, name), ('parent_id.parent_id.parent_id.name', operator, name)]
				])
			return self.search(domain, limit=limit).name_get()
		return super(SaleOrder, self).name_search(name, args, operator, limit)

	# @api.model
	# def name_search(self, name='', args=None, operator='ilike', limit=100):
 #    	if operator in ('ilike', 'like', '=', '=like', '=ilike'):
 #    		print ("name search called *******************")
 #    		domain = expression.AND([
 #                args or [],
 #                ['|', '|', '|', ('name', operator, name), ('parent_id.name', operator, name), ('parent_id.parent_id.name', operator, name), ('parent_id.parent_id.parent_id.name', operator, name)]
 #            ])
 #            return self.search(domain, limit=limit).name_get()
 #        return super(SaleOrder, self).name_search(name, args, operator, limit)