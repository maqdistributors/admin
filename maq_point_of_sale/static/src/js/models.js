odoo.define('maq_point_of_sale.models', function (require) {
    "use strict";

    var rpc = require("web.rpc");
    var models = require('point_of_sale.models');

    // models.load_fields("res.users", ['product_categ_ids']);
    models.load_fields("pos.order", ['customer_verified']);
    models.load_fields('pos.config', ['limit_categories', 'iface_restrict_categ_ids', 'iface_available_child_categ_ids']);

    var PosModelSuper = models.PosModel;
    models.PosModel = models.PosModel.extend({
        initialize: function () {
            var self = this;
            var pos_category_model = _.find(this.models, function (model) {
                return model.model === "pos.category";
            });
            pos_category_model.domain = function (self) {
                var domain = self.config.limit_categories && self.config.iface_restrict_categ_ids.length ? [['id', 'not in', self.config.iface_restrict_categ_ids]] : [];
                return domain;
            };
            var prod_model = _.find(this.models, function (model) {
                return model.model === "product.product";
            });
            prod_model.domain = function (self) {
                var domain = self.config.iface_available_child_categ_ids.length ||  self.config.iface_restrict_categ_ids ? [
                    '&','&',
                    ['sale_ok','=',true],
                    ['available_in_pos','=',true],
                    '|',
                    ['pos_categ_id', '=', false],
                    '&',
                    ['pos_categ_id.id', 'not in', self.config.iface_available_child_categ_ids],
                    ['pos_categ_id.id', 'not in', self.config.iface_restrict_categ_ids]] : [];

                return domain;
            };
            // var product_pricelist_item_model = _.find(this.models, function (model) {
            //     return model.model === "product.pricelist.item";
            // });
            // product_pricelist_item_model.domain = function (self) {
            //     var domain = self.user.product_categ_ids ? [['pricelist_id', 'in', _.pluck(self.pricelists, 'id')],['product_id.categ_id.id', 'not in', self.user.product_categ_ids]] : [];
            //     return domain;
            // };
            PosModelSuper.prototype.initialize.apply(self, arguments);
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