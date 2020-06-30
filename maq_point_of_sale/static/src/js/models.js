odoo.define('maq_point_of_sale.models', function (require) {
    "use strict";

    var models = require('point_of_sale.models');

    models.load_fields("pos.order", ["customer_verified"]);
    var _super_order = models.Order.prototype;
    models.Order = models.Order.extend({
        initialize: function (session, attributes) {
            _super_order.initialize.apply(this, arguments);
            this.customer_verified = this.customer_verified || false;
        },
        init_from_JSON: function (json) {
            _super_order.init_from_JSON.apply(this, arguments);
            this.customer_verified = json.customer_verified || false;
        },
        export_as_JSON: function () {
            var json = _super_order.export_as_JSON.apply(this, arguments);
            json.customer_verified = this.get_customer_verified();
            return json;
        },
        apply_ms_data: function (data) {
            if (_super_order.apply_ms_data) {
                _super_order.apply_ms_data.apply(this, arguments);
            }
            this.customer_verified = data.customer_verified || false;
        },
        get_customer_verified() {
            return this.customer_verified;
        },
        set_customer_verified(customer_verified) {
            this.customer_verified = customer_verified;
        },
    });
});