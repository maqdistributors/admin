odoo.define('maq_point_of_sale.popups', function (require) {
    "use strict";

    var PopupWidget = require('point_of_sale.popups');
    var gui = require('point_of_sale.gui');
    var CheckBoxPopupWidget = PopupWidget.extend({
        template: 'CheckBoxPopupWidget',
        show: function (options) {
            var self = this;
            options = options || {};
            this._super(options);
            this.renderElement();
            this.$('input,textarea').focus();
            var value = self.pos.get_order().customer_verified;
            if (value === true) {
                this.$('input,textarea').prop("checked", true);
            }
        },
        click_confirm: function () {
            var value = this.$('input,textarea').is(":checked");
            this.gui.close_popup();
            if (this.options.confirm) {
                this.options.confirm.call(this, value);
            }
        },
        click_cancel: function () {
            var self = this;
            this._super(arguments);
            this.$('input,textarea').prop("checked", false);
            self.pos.get_order().customer_verified = false;
            this.gui.close_popup();
            if (this.options.cancel) {
                this.options.cancel.call(this);
            }
        },
    });
    gui.define_popup({name: 'checkbox', widget: CheckBoxPopupWidget});
    return PopupWidget;
});
