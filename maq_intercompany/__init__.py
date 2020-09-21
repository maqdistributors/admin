# -*- coding: utf-8 -*-

from . import models

from odoo.api import Environment, SUPERUSER_ID


def uninstall_hook(cr, registry):
    ''' Write the uninstall hook to reset the conditions of the record rules
        back to original
    '''
    env = Environment(cr, SUPERUSER_ID, {})
    rule_id = env.ref("base.res_company_rule_erp_manager")
    if rule_id.groups:
        rule_id.update({'groups':[(3,rule_id.groups.id)]})
    if not rule_id.groups:
        rule_id.update({'groups':[(6, 0, [env.ref('base.group_erp_manager').id])]})
