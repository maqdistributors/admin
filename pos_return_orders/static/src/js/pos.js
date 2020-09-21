odoo.define('pos_return_orders.pos_return_orders', function (require) {
"use strict";

var screens = require('point_of_sale.screens');
var core = require('web.core');
var PosPopWidget = require('point_of_sale.popups');
var gui = require('point_of_sale.gui');
var rpc = require('web.rpc');
var models = require('point_of_sale.models');
var pos_orders_lists = require('pos_orders_lists.pos_orders_lists');
var _t = core._t;

    pos_orders_lists.OrderListScreenWidget.include({
        renderElement: function() {
            var self = this;
            this._super();
            this.$('.client-list-contents').delegate('.wv_return_button','click',function(event){
                var order_id = $(this).data('id');
                    rpc.query({
                        model: 'pos.order',
                        method: 'search_return_orders',
                        args: [order_id],
                    }).then(function(result){
                        if(result != undefined){
                            self.gui.show_popup('pos-order-return',result);
                        }
                        else{
                            alert("Your Order Id is not valid");
                        }
                    },function(err,event){
                        event.preventDefault();
                        self.gui.show_popup('error',{
                            'title': _t('Error'),
                            'body': _t('Your Internet connection is probably down.'),
                        });
                    });
            });
        },
    });

    var PosOrderReturnWidget = PosPopWidget.extend({
        template: 'PosOrderReturnWidget',
	    
        renderElement: function(options){
            this._super();
            var self = this;
            var selectedOrder = this.pos.get_order();
            this.$('.return_all_order_button').click(function(){
            	var order_id = $(this).data('order_id');
            	var order_name = $(this).data('order_name');

           		$.each($(".return_product_qty"), function(index, value) {
				 	var qty = $(this).data('qty');
				 	var discount = $(this).data('discount');
				 	var line_id = $(this).data('line_id');
				 	var product_id = $(this).data('product-id');
				 	var price_unit = $(this).data('price_unit');
				 	var product = self.pos.db.get_product_by_id(product_id);
                	selectedOrder.add_product(product, {
                        quantity: parseFloat(qty),
                        price: - price_unit,
                        discount: discount,
                    });
                    selectedOrder.selected_orderline.db_line_id = line_id;
            	});
            	selectedOrder.order_id = order_id;
                selectedOrder.order_name = order_name;
            	self.gui.show_screen('products');
	        });
	        this.$('.return_order_button').click(function(){
	        	var order_id = $(this).data('order_id');
            	var order_name = $(this).data('order_name');
           		$.each($(".return_product_qty"), function(index, value) {
				 	var qty = $(this).val();
				 	var discount = $(this).data('discount');
				 	var line_id = $(this).data('line_id');
				 	var product_id = $(this).data('product-id');
				 	var price_unit = $(this).data('price_unit');
				 	var product = self.pos.db.get_product_by_id(product_id);
				 	if(parseFloat(qty) > 0){
	                	selectedOrder.add_product(product, {
	                        quantity: - parseFloat(qty),
	                        price: price_unit,
	                        discount: discount,
	                    });                    
	                    selectedOrder.selected_orderline.db_line_id = line_id;
	                }
            	});
            	selectedOrder.order_id = order_id;
                selectedOrder.order_name = order_name;
            	self.gui.show_screen('products');
	        });
        },
        show: function(options){
            this.options = options || {};
            var self = this;
            this._super(options); 
            this.renderElement(options);
        },
    });

    gui.define_popup({
        'name': 'pos-order-return', 
        'widget': PosOrderReturnWidget,
    });

    var _super_order = models.Order.prototype;
    models.Order = models.Order.extend({
        export_as_JSON: function() {
            var json = _super_order.export_as_JSON.apply(this,arguments);
            json.reference_number = this.uid.replace(/-/g, '');
            json.order_id = this.order_id || 0;
            json.order_name = this.order_name||0;
            return json;
        },
        init_from_JSON: function(json) {
            _super_order.init_from_JSON.apply(this,arguments);
            this.reference_number = json.uid.replace(/-/g, '');
            this.order_id = '' ;
            this.order_name = '';
        },
        export_for_printing: function(){
        	var json = _super_order.export_for_printing.apply(this);
        	json.order_id = this.order_id || false;
            json.order_name = this.order_name|| false;
            return json;
        },
    });

    var OrderlineSuper = models.Orderline;
    models.Orderline = models.Orderline.extend({
        initialize: function(){
            var self = this;
            self.order_line_id = 0;
            OrderlineSuper.prototype.initialize.apply(this, arguments);   
        },
        export_as_JSON: function(){
            var data = OrderlineSuper.prototype.export_as_JSON.apply(this, arguments);
            data.order_line_id = this.db_line_id || 0;
            return data;
        }
    });
});

