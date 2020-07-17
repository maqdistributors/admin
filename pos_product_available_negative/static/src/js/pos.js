/*  Copyright 2016 Stanislav Krotov <https://it-projects.info/team/ufaks>
    Copyright 2018-2019 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
    License MIT (https://opensource.org/licenses/MIT). */
odoo.define("pos_product_available_negative.pos", function (require) {
    "use strict";

    var screens = require("point_of_sale.screens");
    var models = require("point_of_sale.models");
    var core = require("web.core");
    var _t = core._t;

    var _super_orderline = models.Orderline.prototype;
    models.Orderline = models.Orderline.extend({
        initialize: function (json) {
            _super_orderline.initialize.apply(this, arguments);
            this.notify_qty = false;
        },
    });

    var _super_order = models.Order.prototype;
    models.Order = models.Order.extend({
        export_as_JSON: function () {
            var json = _super_order.export_as_JSON.apply(this, arguments);
            json.negative_stock_user_id = this.negative_stock_user_id
                ? this.negative_stock_user_id.id
                : false;
            return json;
        },
    });
    screens.OrderWidget.include({
        set_value: function (val) {
            this._super();
            var order = this.pos.get_order();
            if (order.get_selected_orderline()) {
                var mode = this.numpad_state.get('mode');
                if (mode === 'quantity') {
                    if (val != "" && val != "remove") {
                        if (!order.get_selected_orderline().notify_qty) {
                            var qty_available = order.get_selected_orderline().product.qty_available;
                            if (val > qty_available) {
                                this.gui.show_popup("alert", {
                                    title: _t("STOCK CHECK WARNING"),
                                    body: _t("This product quantity may be unavailable" +
                                        "Please verity the product quantity available and notify a supervisor of any discrepancies."),
                                });
                                order.get_selected_orderline().notify_qty = true;
                            }
                        }
                    }
                    order.get_selected_orderline().set_quantity(val);
                } else if (mode === 'discount') {
                    order.get_selected_orderline().set_discount(val);
                } else if (mode === 'price') {
                    var selected_orderline = order.get_selected_orderline();
                    selected_orderline.price_manually_set = true;
                    selected_orderline.set_unit_price(val);
                }
            }
        },
    });
    screens.ProductListWidget.include({
        init: function (parent, options) {
            var self = this;
            this._super(parent, options);
            if (!this.pos.config.negative_order_warning) {
                return;
            }

            var click_product_handler_super = this.click_product_handler;
            this.click_product_handler = function () {
                var product = self.pos.db.get_product_by_id(this.dataset.productId);
                var order = self.pos.get_order();
                if (order.get_selected_orderline()) {
                    if (!order.get_selected_orderline().notify_qty) {
                        if (order.get_selected_orderline().quantity + 1 > order.get_selected_orderline().product.qty_available) {
                            self.gui.show_popup("alert", {
                                title: _t("STOCK CHECK WARNING"),
                                body: _t("This product quantity may be unavailable" +
                                    "Please verity the product quantity available and notify a supervisor of any discrepancies."),
                            });
                            order.get_selected_orderline().notify_qty = true;
                        }
                    }
                }
                if (product.type === "product" && product.qty_available <= 0) {
                    self.gui.show_popup("alert", {
                        title: _t("STOCK CHECK WARNING"),
                        body: _t("This product quantity may be unavailable" +
                            "Please verity the product quantity available and notify a supervisor of any discrepancies."),
                    });
                }
                _.bind(click_product_handler_super, this)();
            };
        },
    });
});
