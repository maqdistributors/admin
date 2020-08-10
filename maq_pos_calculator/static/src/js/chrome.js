odoo.define('maq_pos_calculator.chrome', function (require) {
    "use strict";

    var chrome = require('point_of_sale.chrome');
    var PosBaseWidget = require('point_of_sale.BaseWidget');

    var OrderWeightWidget = PosBaseWidget.extend({
        template: 'OrderWeightWidget',
        init: function (parent, options) {
            var self = this;
            this._super(parent, options);
            this.pos.get('orders').bind('add remove change', this.change_selected_order, this);
            this.pos.bind('change:selectedOrder', this.change_selected_order, this);
            self.change_selected_order();
            self.bind_order_events();
            self.renderElement();
        },
        change_selected_order: function () {
            var self = this;
            if (self.pos.get_order()) {
                self.bind_order_events();
                self.renderElement();
            }
        },
        bind_order_events: function () {
            var self = this;
            var order = this.pos.get_order();
            order.unbind('change:client', this.renderElement, this);
            order.bind('change:client', this.renderElement, this);
            order.unbind('change', this.renderElement, this);
            order.bind('change', this.renderElement, this);

            var lines = order.orderlines;
            lines.unbind('add', this.renderElement, this);
            lines.bind('add', this.renderElement, this);
            lines.unbind('remove', this.renderElement, this);
            lines.bind('remove', this.renderElement, this);
            lines.unbind('change', this.renderElement, this);
            lines.bind('change', this.renderElement, this);

        },
        renderElement: function () {
            var self = this;
            self._super();
            self.pos.purchase_weight_limit = self.pos.config.cannabis_purchase_limit.toFixed(3);
            var order = this.pos.get_order();
            if (!order) {
                return;
            }
            var orderlines = order.get_orderlines();
            order.ordered_cannabis = 0.0;
            for (var i = 0, len = orderlines.length; i < len; i++) {
                order.ordered_cannabis += orderlines[i].quantity * orderlines[i].product.equivalent_weight;
            }
            order.ordered_cannabis = order.ordered_cannabis.toFixed(3);
        },
    });

    chrome.Chrome.include({
        build_widgets: function () {
            this.widgets.push({
                'name': 'order_weight_details',
                'widget': OrderWeightWidget,
                'replace': '.placeholder-OrderWeightWidget'
            });
            this._super();
        },
    });
    return {
        OrderWeightWidget: OrderWeightWidget,
    };
});