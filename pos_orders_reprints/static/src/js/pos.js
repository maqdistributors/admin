odoo.define('pos_orders_reprints.pos_orders_reprints', function (require) {
"use strict";

    var module = require('point_of_sale.models');
    var screens = require('point_of_sale.screens');
    var gui = require('point_of_sale.gui');
    var PosPopWidget = require('point_of_sale.popups');
    var core = require('web.core');
    var rpc = require('web.rpc');
    var pos_orders = require('pos_orders_lists.pos_orders_lists');
    var QWeb = core.qweb;
    var _t = core._t;

    var OrdersReceiptScreenWidget = screens.ReceiptScreenWidget.extend({
        template: 'OrdersReceiptScreenWidget',
        click_next: function(){
            this.gui.show_screen('products');
        },
        click_back: function(){
            this.gui.show_screen('products');
        },
        render_receipt: function(){
            self = this;
            var order = self.pos.get_order();
            self.$('.pos-receipt-container').html(order.receipt_reprint_val);
            order.receipt_reprint_val = "";
        },
        print_web: function(){
            window.print();
        },
    });

    gui.define_screen({name:'wv-orders-receipt', widget: OrdersReceiptScreenWidget});
    
    pos_orders.PosOrderPopupWidget.include({
    template: 'PosOrderPopupWidget',
        renderElement: function(){
            this._super(); 
            var self = this;
            $(".print_normal_printer").click(function(){
                var order_id = $(this).data('id');
                rpc.query({
                    model: 'pos.config',
                    method: 'get_order_detail',
                    args: [order_id],
                }).then(function(result){
                    var order = self.pos.get_order();
                    order.receipt_reprint_val = QWeb.render('PosTicketReprint',{
                        widget:self,
                        order: result.order,
                        change: result.change,
                        orderlines: result.order_line,
                        amount_subtotal:result.amount_subtotal,
                        discount_total: result.discount,
                        paymentlines: result.payment_lines,
                        receipt: order.export_for_printing(),
                        tax_lines:result.tax_lines,
                    });
                    self.gui.show_screen('wv-orders-receipt');
                });
            }); 
            $(".print_thermal_printer").click(function(){
                var order_id = $(this).data('id');
                rpc.query({
                    model: 'pos.config',
                    method: 'get_order_detail',
                    args: [order_id],
                }).then(function(result){
                    var order = self.pos.get_order();
                    var env = {
                        widget:  self,
                        receipt: self.pos.get_order().export_for_printing(),
                        order: result.order,
                        orderlines: result.order_line,
                        amount_subtotal:result.amount_subtotal,
                        change: result.change,
                        discount_total: result.discount,
                        paymentlines: result.payment_lines,
                        tax_lines:result.tax_lines,
                    };
                    var receipt = QWeb.render('XmlReceiptCopy',env);
                    self.pos.proxy.print_receipt(receipt);
                });
            });
        },
    });    
});
