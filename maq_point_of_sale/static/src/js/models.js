odoo.define('maq_point_of_sale.models', function (require) {
    "use strict";

    var models = require('point_of_sale.models');

    models.load_fields({model: "pos.order", fields: ["customer_verified"]});
    var PosModelSuper = models.PosModel;
    models.PosModel = models.PosModel.extend({
        initialize: function () {
            var self = this;
            var pos_category_model = _.find(this.models, function (model) {
                return model.model === "pos.category";
            });
            pos_category_model.domain = function (self) {
                var domain = self.config.limit_categories && self.config.iface_available_categ_ids.length ? [['id', 'not in', self.config.iface_available_categ_ids]] : [];
                return domain;
            };
            var product_product_model = _.find(this.models, function (model) {
                return model.model === "product.product";
            });
            product_product_model.domain = function (self) {
                var domain = ['&', '&', ['sale_ok', '=', true], ['available_in_pos', '=', true], '|', ['company_id', '=', self.config.company_id[0]], ['company_id', '=', false]];
                if (self.config.limit_categories && self.config.iface_available_categ_ids.length) {
                    domain.unshift('&');
                    domain.push(['pos_categ_id', 'not in', self.config.iface_available_categ_ids]);
                }
                if (self.config.iface_tipproduct) {
                    domain.unshift(['id', '=', self.config.tip_product_id[0]]);
                    domain.unshift('|');
                }
                return domain;
            };
            PosModelSuper.prototype.initialize.apply(this, arguments);
        },
    });

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