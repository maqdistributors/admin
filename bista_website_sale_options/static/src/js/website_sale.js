odoo.define('bista_website_sale_options.website_sale_options', function (require) {
    "use strict";
    var ajax = require('web.ajax');
    var Dialog = require('web.Dialog');
    var weContext = require('web_editor.context');
    var core = require('web.core');
    var _t = core._t;
    var OptionalProductsModal = require('sale.OptionalProductsModal');
    OptionalProductsModal.include({
        /**
         * @override
         */
        /**
         * @override
         */
        willStart: function () {
            var self = this;

            var uri = this._getUri("/product_configurator/show_optional_products");
            var getModalContent = ajax.jsonRpc(uri, 'call', {
                product_id: self.rootProduct.product_id,
                variant_values: self.rootProduct.variant_values,
                pricelist_id: self.pricelistId || false,
                add_qty: self.rootProduct.quantity,
                kwargs: {
                    context: _.extend({
                        'quantity': self.rootProduct.quantity
                    }, weContext.get()),
                }
            })
                .then(function (modalContent) {
                    if (modalContent) {
                        var $modalContent = $(modalContent);
                        $modalContent = self._postProcessContent($modalContent);
                        self.$content = $modalContent;
                    } else {
                        self.trigger('options_empty');
                        self.preventOpening = true;
                    }
                    setTimeout(function () {
                        $('.modal-footer button.btn-secondary').trigger('click');
                    }, 3000);
                    setTimeout(function () {
                        self.container[0].className = "";
                    }, 3000);
                });

            var parentInit = self._super.apply(self, arguments);
            return $.when(getModalContent, parentInit);
        },
    });
});
