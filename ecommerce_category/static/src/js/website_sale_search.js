
odoo.define('ecommerce_category.product_advance_search', function (require) {
    'use strict';

    $(function () {
        if($(".oe_search_box")){
            var searchBox = $(".oe_search_box");
            // remove querystring values from the url and redirect user to the cliked category only.
            $('#o_shop_collapse_category li>a').click(function(event){
                event.preventDefault();
                event.stopPropagation();
                if (searchBox.parents('form').data('search-all')) {
                    searchBox.val('');
                    window.location = $(event.currentTarget).attr('href').split('?')[0];
                } else  {
                    window.location = $(event.currentTarget).attr('href');
                }
            });
        }
    });
});