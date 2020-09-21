# -*- coding: utf-8 -*-

{
    'name': 'MAQ POS',
    'version': '1.0',
    'summary': 'Imporvements in POS Usability',
    'description': """
    Following features will be added
    Req Id. 1.82 - Cash control access during taking money out or putting money back
    Req Id. 1.83 - Record cash control in POS order for each transactions of taking money out or putting money back
    Req Id. 1.84 - Access rights to show Amount in POS Session
    Req Id. 2.01 - Access rights for opening session in POS
    """,
    'depends': ['point_of_sale'],
    'category': 'Point Of Sale',
    'data': [
        'security/res_groups.xml',
        'security/ir.model.access.csv',
        'views/pos_append_view.xml',
        'views/access_session_view.xml',
        'wizards/inherit_pos_box.xml',
        'wizards/inherit_pos_session_view.xml'
    ],
    'demo': [],
    'qweb': ['static/src/xml/inherit_pos.xml'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
