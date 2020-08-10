odoo.define('maq_pos_calculator.screens', function (require) {
    "use strict";

    var screen = require('maq_point_of_sale.screens');
    var core = require('web.core');
    var _t = core._t;

    var ActionpadWidget = screen.ActionpadWidget;

    ActionpadWidget.include({
        renderElement: function () {
            var self = this;
            self._super();
            this.$('.pay').off('click').on('click', function () {
                var order = self.pos.get_order();
                var has_valid_product_lot = _.every(order.orderlines.models, function (line) {
                    return line.has_valid_product_lot();
                });
                if (!has_valid_product_lot) {
                    self.gui.show_popup('confirm', {
                        'title': _t('Empty Serial/Lot Number'),
                        'body': _t('One or more product(s) required serial/lot number.'),
                        confirm: function () {
                            var config = self.pos.config.payment_confirmation_box;
                            if (config === true) {
                                this.gui.show_popup('checkbox', {
                                    'title': _t('Has this customers ID been verified ?'),
                                    confirm: function () {
                                        var value = this.$('input,textarea').is(":checked");
                                        self.pos.get_order().customer_verified = value;
                                        if (value === true) {
                                            var order = self.pos.get_order();
                                            if (order.ordered_cannabis > self.pos.config.cannabis_purchase_limit) {
                                                this.gui.show_popup("WarningalertMsg", {
                                                    title: _t("CANNABIS WEIGHT CHECK WARNING"),
                                                    body: _t('Your Cart Contain more then allowed Cannabis Weight'),
                                                    msg: _t('Please Adjust your cart item to Cannabis Weight to process payment.'),
                                                });
                                                return false;
                                            }
                                            self.gui.show_screen('payment');
                                        }
                                        return false;
                                    },
                                });
                            } else {
                                var order = self.pos.get_order();
                                if (order.ordered_cannabis > self.pos.config.cannabis_purchase_limit) {
                                    this.gui.show_popup("WarningalertMsg", {
                                        title: _t("CANNABIS WEIGHT CHECK WARNING"),
                                        body: _t('Your Cart Contain more then allowed Cannabis Weight'),
                                        msg: _t('Please Adjust your cart item to Cannabis Weight to process payment.'),
                                    });
                                    return false;
                                }else{
                                    self.gui.show_screen('payment');
                                }
                            }
                        },
                    });
                } else {
                    var config = self.pos.config.payment_confirmation_box;
                    if (config === true) {
                        self.pos.gui.show_popup('checkbox', {
                            'title': _t('Has this customers ID been verified ?'),
                            confirm: function () {
                                var value = this.$('input,textarea').is(":checked");
                                self.pos.get_order().customer_verified = value;
                                if (value === true) {
                                    var order = self.pos.get_order();
                                    if (order.ordered_cannabis > self.pos.config.cannabis_purchase_limit) {
                                        this.gui.show_popup("WarningalertMsg", {
                                            title: _t("CANNABIS WEIGHT CHECK WARNING"),
                                            body: _t('Your Cart Contain more then allowed Cannabis Weight'),
                                            msg: _t('Please Adjust your cart item to Cannabis Weight to process payment.'),
                                        });
                                        return false;
                                    }
                                    self.gui.show_screen('payment');
                                }
                                return false;
                            },
                        });
                    } else {
                        var order = self.pos.get_order();
                        if (order.ordered_cannabis > self.pos.config.cannabis_purchase_limit) {
                            self.gui.show_popup("WarningalertMsg", {
                                title: _t("CANNABIS WEIGHT CHECK WARNING"),
                                body: _t('Your Cart Contain more then allowed Cannabis Weight'),
                                msg: _t('Please Adjust your cart item to Cannabis Weight to process payment.'),
                            });
                            return false;
                        }
                        else{
                            self.gui.show_screen('payment');
                        }
                    }
                }
            });
            this.$('.set-customer').click(function () {
                self.gui.show_screen('clientlist');
            });
        },
    });
});
