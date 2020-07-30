/*  Copyright 2016 Stanislav Krotov <https://it-projects.info/team/ufaks>
    Copyright 2018-2019 Kolushov Alexandr <https://it-projects.info/team/KolushovAlexandr>
    License MIT (https://opensource.org/licenses/MIT). */
odoo.define("pos_product_available_negative.pos", function (require) {
    "use strict";

    var screens = require("point_of_sale.screens");
    var models = require("point_of_sale.models");
    var core = require("web.core");
    var _t = core._t;
    var PopupWidget = require('point_of_sale.popups');
    var gui = require('point_of_sale.gui');

    var PackLotLinePopupWidget = PopupWidget.extend({
        template: 'PackLotLinePopupWidget',
        click_confirm: function () {
            var pack_lot_lines = this.options.pack_lot_lines;
            this.$('.packlot-line-input').each(function (index, el) {
                var cid = $(el).attr('cid'),
                    lot_name = $(el).val();
                var pack_line = pack_lot_lines.get({cid: cid});
                pack_line.set_lot_name(lot_name);
            });
            pack_lot_lines.remove_empty_model();
            pack_lot_lines.set_quantity_by_lot();
            this.options.order.save_to_db();
            this.options.order_line.trigger('change', this.options.order_line);
            this.gui.close_popup();
            if (pack_lot_lines.order_line.product.type === "product" && pack_lot_lines.order_line.product.qty_available <= 0) {
                this.pos.gui.show_popup("alertMsg", {
                    title: _t("STOCK CHECK WARNING"),
                    body: _t('This product quantity may be unavailable'),
                    msg: _t('Please verify the product quantity available and notify a supervisor of any discrepancies.'),
                });
                pack_lot_lines.order_line.notify_qty = true;
            }
        },
        click_cancel: function () {
            this.gui.close_popup();
            if (this.options.cancel) {
                this.options.cancel.call(this);
            }
            var pack_lot_lines = this.options.pack_lot_lines;
            if (pack_lot_lines.order_line.product.type === "product" && pack_lot_lines.order_line.product.qty_available <= 0) {
                this.pos.gui.show_popup("alertMsg", {
                    title: _t("STOCK CHECK WARNING"),
                    body: _t('This product quantity may be unavailable'),
                    msg: _t('Please verify the product quantity available and notify a supervisor of any discrepancies.'),
                });
                pack_lot_lines.order_line.notify_qty = true;
            }
        },
    });
    gui.define_popup({name: 'packlotline', widget: PackLotLinePopupWidget});

    var CustomMsgPopupWidget = PopupWidget.extend({
        template: 'CustomMsgPopupWidget',
        show: function (options) {
            options = options || {};
            this._super(options);
            this.renderElement();
        },
    });
    gui.define_popup({name: 'alertMsg', widget: CustomMsgPopupWidget});

    var _super_orderline = models.Orderline.prototype;
    models.Orderline = models.Orderline.extend({
        initialize: function (json) {
            _super_orderline.initialize.apply(this, arguments);
            this.notify_qty = false;
        },
        export_as_JSON: function () {
            var json = _super_orderline.export_as_JSON.apply(this, arguments);
            json.notify_qty = this.notify_qty
            return json;
        },
    });

    var _super_order = models.Order.prototype;
    models.Order = models.Order.extend({
        add_product: function (product, options) {
            if (this._printed) {
                this.destroy();
                return this.pos.get_order().add_product(product, options);
            }
            this.assert_editable();
            options = options || {};
            var attr = JSON.parse(JSON.stringify(product));
            attr.pos = this.pos;
            attr.order = this;
            var line = new models.Orderline({}, {pos: this.pos, order: this, product: product});

            if (options.quantity !== undefined) {
                line.set_quantity(options.quantity);
            }

            if (options.price !== undefined) {
                line.set_unit_price(options.price);
            }

            //To substract from the unit price the included taxes mapped by the fiscal position
            this.fix_tax_included_price(line);

            if (options.discount !== undefined) {
                line.set_discount(options.discount);
            }

            if (options.extras !== undefined) {
                for (var prop in options.extras) {
                    line[prop] = options.extras[prop];
                }
            }

            var to_merge_orderline;
            for (var i = 0; i < this.orderlines.length; i++) {
                if (this.orderlines.at(i).can_be_merged_with(line) && options.merge !== false) {
                    to_merge_orderline = this.orderlines.at(i);
                }
            }
            if (to_merge_orderline) {
                if (!to_merge_orderline.notify_qty) {
                    if (to_merge_orderline.product.type === "product") {
                        if (to_merge_orderline.quantity + 1 > line.product.qty_available) {
                            this.pos.gui.show_popup("alertMsg", {
                                title: _t("STOCK CHECK WARNING"),
                                body: _t('This product quantity may be unavailable'),
                                msg: _t('Please verify the product quantity available and notify a supervisor of any discrepancies.'),
                            });
                            to_merge_orderline.notify_qty = true;
                        }
                    }
                }
                to_merge_orderline.merge(line);
            } else {
                this.orderlines.add(line);
            }
            this.select_orderline(this.get_last_orderline());

            if (line.has_product_lot) {
                this.display_lot_popup();
            }
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
                        if (order.get_selected_orderline().product.type === "product") {
                            if (!order.get_selected_orderline().notify_qty) {
                                var qty_available = order.get_selected_orderline().product.qty_available;
                                if (val > qty_available) {
                                    this.gui.show_popup("alertMsg", {
                                        title: _t("STOCK CHECK WARNING"),
                                        body: _t('This product quantity may be unavailable'),
                                        msg: _t('Please verify the product quantity available and notify a supervisor of any discrepancies.'),
                                    });
                                    order.get_selected_orderline().notify_qty = true;
                                }
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
                if (product.type === "product" && product.qty_available <= 0) {
                    self.gui.show_popup("alertMsg", {
                        title: _t("STOCK CHECK WARNING"),
                        body: _t('This product quantity may be unavailable'),
                        msg: _t('Please verify the product quantity available and notify a supervisor of any discrepancies.'),
                    });
                } else if (product.type === "product") {
                    if (order.get_selected_orderline() !== undefined) {
                        if (order.get_selected_orderline().product.id === product.id) {
                            if (!order.get_selected_orderline().notify_qty) {
                                if (order.get_selected_orderline().quantity + 1 > order.get_selected_orderline().product.qty_available) {
                                    self.gui.show_popup("alertMsg", {
                                        title: _t("STOCK CHECK WARNING"),
                                        body: _t('This product quantity may be unavailable'),
                                        msg: _t('Please verify the product quantity available and notify a supervisor of any discrepancies.'),
                                    });
                                    order.get_selected_orderline().notify_qty = true;
                                }
                            }
                        }
                    }
                }
                _.bind(click_product_handler_super, this)();
            };
        },
    });
});
