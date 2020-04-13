odoo.define('maq_website_sale.add_to_cart_b', function (require) {
'use strict';

var ajax = require('web.ajax');
require('web.dom_ready');
var weContext = require("web_editor.context");
require('website_sale.website_sale');

   $('.oe_website_sale #add_to_cart_b')
   .off('click')
   .removeClass('b-submit')
   .click(function (event) {
       event.preventDefault();

       var $form = $(this).closest('form');

       var qty_input = $form.find('input.quantity');

       var data = [];

       for(var i=0; i < qty_input.length; i++){
           console.log(qty_input[i]);
           if(qty_input[i].value != 0){
               data.push({
                   'product_id' : qty_input[i].name,
                   'quantity' : qty_input[i].value
               });
           }
       }

       $.each(data, function(i, val){
           var quantity = parseFloat(val['quantity']);
           var product_id = parseInt(val['product_id'], 10);
           $form.ajaxSubmit({
               url:  '/shop/cart/update_option',
               data: {lang: weContext.get().lang, product_id: product_id, add_qty:quantity},
               success: function (quantity) {
                   var $q = $(".my_cart_quantity");
                   $q.parent().parent().removeClass("hidden", !quantity);
                   $q.html(quantity).hide().fadeIn(600);

               }
           });
       });
		
		$form[0].reset();

   });

   $('.oe_website_sale').on('click', 'tr.variant_details label[label-default="label-default"]', function (ev) {
       var product_id = $(ev.target).closest('tr.variant_details')[0].id;
       console.log(product_id);
       $('.oe_website_sale').find('label.active').each(function () {
           this.style.color = "#555555";
           this.className = '';
       });
       this.style.color = "#1ad68f";
       this.className = 'active';
       update_product_image(this, product_id);
   });

   function update_product_image(event_source, product_id) {
       var $img;
       if ($('#o-carousel-product').length) {
           $img = $(event_source).closest('tr.js_product, .oe_website_sale').find('img.js_variant_img');
           $img.attr("src", "/web/image/product.product/" + product_id + "/image");
           $img.parent().attr('data-oe-model', 'product.product').attr('data-oe-id', product_id)
               .data('oe-model', 'product.product').data('oe-id', product_id);

           var $thumbnail = $(event_source).closest('tr.js_product, .oe_website_sale').find('img.js_variant_img_small');
           if ($thumbnail.length !== 0) { // if only one, thumbnails are not displayed
               $thumbnail.attr("src", "/web/image/product.product/" + product_id + "/image/90x90");
               $('.carousel').carousel(0);
           }
       }
       else {
           $img = $(event_source).closest('tr.js_product, .oe_website_sale').find('span[data-oe-model^="product."][data-oe-type="image"] img:first, img.product_detail_img');
           $img.attr("src", "/web/image/product.product/" + product_id + "/image");
           $img.parent().attr('data-oe-model', 'product.product').attr('data-oe-id', product_id)
               .data('oe-model', 'product.product').data('oe-id', product_id);
       }
       // reset zooming constructs
       $img.filter('[data-zoom-image]').attr('data-zoom-image', $img.attr('src'));
       if ($img.data('zoomOdoo') !== undefined) {
           $img.data('zoomOdoo').isReady = false;
       }
   }

});

// odoo.define('maq_custom_theme.add_to_cart_b', function (require) {
//     'use strict';

//     require('web.dom_ready');
//     var weContext = require("web_editor.context");
//     require('website_sale.website_sale');

//     $('.oe_website_sale #add_to_cart_b')
//         .off('click')
//         .removeClass('b-submit')
//         .click(function (event) {
//             event.preventDefault();

//             var $form = $(this).closest('form');

//             var qty_input = $form.find('input.quantity:not([disabled])');

//             var data = [];
//             var $modal = "<div id=\"modal_products_notification\" class=\"modal fade\" tabindex=\"-1\" role=\"dialog\" aria-labelledby=\"myModalLabel\">\n" +
//                 "            <div class=\"modal-dialog modal-md\">\n" +
//                 "                <div class=\"modal-content\">\n" +
//                 "                    <div class=\"modal-header\">\n" +
//                 "                        <button type=\"button\" class=\"close\" data-dismiss=\"modal\" aria-hidden=\"true\">x</button>\n" +
//                 "                        <h2 class=\"modal-title\" id=\"myModalLabel\">Add to Cart Update</h2>\n" +
//                 "                    </div>\n" +
//                 "                    <div class=\"modal-body\">\n" +
//                 "                        <p id='product-detail-model'/>\n" +
//                 "                        <h3>THE SELECTED PRODUCTS HAVE BEEN ADDED TO CART</h3>\n" +
//                 "                    </div>\n" +
//                 "                </div>\n" +
//                 "            </div>\n" +
//                 "        </div>\n";


//             for (var i = 0; i < qty_input.length; i++) {
//                 if (qty_input[i].value <= 0) {
//                     continue;
//                 } else {
//                     data.push({
//                         'product_id': qty_input[i].name,
//                         'quantity': qty_input[i].value
//                     });
//                 }
//             }
//             if (data.length > 0) {
//                 $($modal).appendTo($form)
//                     .modal()
//                     .on('hide.bs.modal', function () {
//                         $form.removeClass('css_options'); // possibly reactivate opacity (see above)
//                         $(this).remove();
//                     });
//                 setTimeout(function () {
//                     $("#modal_products_notification").remove()
//                 }, 3000);
//                 setTimeout(function () {
//                     $(".modal-backdrop.fade.show").remove()
//                 }, 3000);
//                 setTimeout(function () {
//                     $("body.modal-open").removeClass('modal-open')
//                 }, 3000);
//             }
//             $.each(data, function (i, val) {
//                 var quantity = parseFloat(val['quantity']);
//                 var product_id = parseInt(val['product_id'], 10);
//                 $form.ajaxSubmit({
//                     url: '/shop/cart/update_option',
//                     data: {lang: weContext.get().lang, product_id: product_id, add_qty: quantity},
//                     success: function (quantity) {
//                         var $q = $(".my_cart_quantity");
//                         $q.parent().parent().removeClass("hidden", !quantity);
//                         $q.html(quantity).hide().fadeIn(600);

//                     }
//                 });
//                 return false;
//             });

//             $form[0].reset();

//         });

//     $('.oe_website_sale').on('click', 'tr.variant_details label[label-default="label-default"]', function (ev) {
//         var product_id = $(ev.target).closest('tr.variant_details')[0].id;
//         console.log(product_id);
//         $('.oe_website_sale').find('label.active').each(function () {
//             this.style.color = "#555555";
//             this.className = '';
//         });
//         this.style.color = "#1ad68f";
//         this.className = 'active';
//         update_product_image(this, product_id);
//     });

//     function update_product_image(event_source, product_id) {
//         var $img;
//         if ($('#o-carousel-product').length) {
//             $img = $(event_source).closest('tr.js_product, .oe_website_sale').find('img.js_variant_img');
//             $img.attr("src", "/web/image/product.product/" + product_id + "/image");
//             $img.parent().attr('data-oe-model', 'product.product').attr('data-oe-id', product_id)
//                 .data('oe-model', 'product.product').data('oe-id', product_id);

//             var $thumbnail = $(event_source).closest('tr.js_product, .oe_website_sale').find('img.js_variant_img_small');
//             if ($thumbnail.length !== 0) { // if only one, thumbnails are not displayed
//                 $thumbnail.attr("src", "/web/image/product.product/" + product_id + "/image/90x90");
//                 $('.carousel').carousel(0);
//             }
//         } else {
//             $img = $(event_source).closest('tr.js_product, .oe_website_sale').find('span[data-oe-model^="product."][data-oe-type="image"] img:first, img.product_detail_img');
//             $img.attr("src", "/web/image/product.product/" + product_id + "/image");
//             $img.parent().attr('data-oe-model', 'product.product').attr('data-oe-id', product_id)
//                 .data('oe-model', 'product.product').data('oe-id', product_id);
//         }
//         // reset zooming constructs
//         $img.filter('[data-zoom-image]').attr('data-zoom-image', $img.attr('src'));
//         if ($img.data('zoomOdoo') !== undefined) {
//             $img.data('zoomOdoo').isReady = false;
//         }
//     }

// });
