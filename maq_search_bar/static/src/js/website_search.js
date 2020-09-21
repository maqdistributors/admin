odoo.define('website_search.custom', function (require) {
'use strict';

    var ajax = require('web.ajax');

    $(document).ready(function () {

        $('.as-search input[name="search"]').keyup(function(ev){
            var search_keyword = $(ev.target).val();
            ajax.jsonRpc("/search_result", 'call', {
                'search_keyword':search_keyword
            }).then(function (data){
                if(data){
                    $('#algolia-autocomplete-container .aa-dropdown-menu').removeClass('d-none');
                    $('#algolia-autocomplete-container .aa-dropdown-menu').html(data);
                }
            });
        }).blur(function(ev){
            setTimeout(function(){
                $('#algolia-autocomplete-container .aa-dropdown-menu').addClass('d-none');
            }, 500);
        });
    });
});
