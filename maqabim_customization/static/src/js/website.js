odoo.define('maqabim_website_sale.stick_menu', function (require) {
'use strict';

    $(document).ready(function() {
        var contentPlacement = $('#oe_main_menu_navbar');
        var navbarFixed = $('.navbar-fixed-top');
        var wrapDiv = $('#wrap');

        if (contentPlacement) {
            var divHeight = contentPlacement.height();
            navbarFixed.css('top', divHeight);
        }
        if (wrapDiv) {
            var wrapHeight = navbarFixed.height();
            wrapDiv.css('padding-top', wrapHeight + 'px');
        }
    });

});
