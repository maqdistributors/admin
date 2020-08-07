odoo.define('maq_pos_calculator.popups', function (require) {
    "use strict";

    var PopupWidget = require('point_of_sale.popups');
    var gui = require('point_of_sale.gui');

    var CustomWarningMsgPopupWidget = PopupWidget.extend({
        template: 'CustomWarningMsgPopupWidget',
    });
    gui.define_popup({name: 'WarningalertMsg', widget: CustomWarningMsgPopupWidget});

});
