odoo.define('maq_partner_order_comment.cart', function(require) {
    "use strict";

    var ajax = require('web.ajax');

    $(document).ready(function() {
        'use strict';
        $("#partner_comment").bind("change", function(ev) {
            var partner_comment = $('#partner_comment').val();
            ajax.jsonRpc('/shop/partner_comment/', 'call', {
                'comment': partner_comment
            })
            $("#partner_comment").val(partner_comment);
        });

        $('.oe_website_sale').each(function () {
        	var oe_website_sale = this;
        	$(oe_website_sale).on("change", ".js_quantity[data-product-id]", function () {
            	var $input = $(this);
            	var value = parseInt($input.val() || 0, 10);
                if (isNaN(value)) {
                    value = 1;
                }
            	var line_id = parseInt($input.data('line-id'),10);
            	ajax.jsonRpc("/shop/cart/update_json", 'call', {
            		'line_id': line_id,
            		'product_id': parseInt($input.data('product-id'), 10),
            		'set_qty': value
                }).then(function (data) {
                	if (!data.cart_quantity) {
                		$('.partner_textarea_comment').addClass('hidden');
                	}
                });
        	});
        });
    });
    
});

