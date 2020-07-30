odoo.define('maq_bista_internal_category_restrict.models', function (require) {
    "use strict";

    var rpc = require("web.rpc");
    var models = require('point_of_sale.models');

    models.load_fields("res.users", ['product_categ_ids']);

    var PosModelSuper = models.PosModel;
    models.PosModel = models.PosModel.extend({
        initialize: function () {
            var self = this;
            var product_pricelist_item_model = _.find(this.models, function (model) {
                return model.model === "product.pricelist.item";
            });
            product_pricelist_item_model.domain = function (self) {
                var domain = self.user.product_categ_ids ? [['pricelist_id', 'in', _.pluck(self.pricelists, 'id')],['product_id.categ_id.id', 'not in', self.user.product_categ_ids]] : [];
                return domain;
            };
            PosModelSuper.prototype.initialize.apply(self, arguments);
        },
    });
});