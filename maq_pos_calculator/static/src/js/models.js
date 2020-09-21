odoo.define('maq_pos_calculator.models', function (require) {
    "use strict";

    var models = require('point_of_sale.models');

    models.load_fields('pos.order', ['ordered_cannabis']);
    models.load_fields('pos.config', ['cannabis_purchase_limit']);
    models.load_fields('product.product', ['product_format', 'reporting_weight', 'equivalent_weight']);

    var _super_order = models.Order.prototype;
    models.Order = models.Order.extend({
        initialize: function (session, attributes) {
            _super_order.initialize.apply(this, arguments);
            this.ordered_cannabis = this.ordered_cannabis || 0.0;
        },
        init_from_JSON: function (json) {
            _super_order.init_from_JSON.apply(this, arguments);
            this.ordered_cannabis = json.ordered_cannabis || 0.0;
        },
        export_as_JSON: function () {
            var json = _super_order.export_as_JSON.apply(this, arguments);
            json.ordered_cannabis = this.get_ordered_cannabis();
            return json;
        },
        apply_ms_data: function (data) {
            if (_super_order.apply_ms_data) {
                _super_order.apply_ms_data.apply(this, arguments);
            }
            this.ordered_cannabis = data.ordered_cannabis || 0.0;
        },
        get_ordered_cannabis() {
            return this.ordered_cannabis;
        },
        set_ordered_cannabis(ordered_cannabis) {
            this.ordered_cannabis = ordered_cannabis;
        },
    });
});
