odoo.define('maqabim_website_popup.maqabim_website_popup', function (require) {
    "use strict";

var ajax = require('web.ajax');
var core = require('web.core');
var base = require('web_editor.base');

var qweb = core.qweb;

ajax.loadXML('/maqabim_website_popup/static/src/xml/maqabim_website_popup.xml', qweb).then(function() {
    var status_welcome = $(qweb.render("maqabim_website_popup.status_welcome", {'website': $('html').data('website-id'), 'company': $('html').data('oe-company-name')}));

    function getCookie(cname) {
        var name = cname + "=";
        var ca = document.cookie.split(';');
        for(var i = 0; i < ca.length; i++) {
            var c = ca[i];
            while (c.charAt(0) == ' ') {
                c = c.substring(1);
            }
            if (c.indexOf(name) == 0) {
                return c.substring(name.length, c.length);
            }
        }
        return "";
    }

    if(getCookie('is_Adult') == 'false' || getCookie('is_Adult') == ''){
      $('body').append(status_welcome).modal('show');
      $('#myModalWelcome').css("display", "block");
      $('#myModalWelcome').css("opacity", "1");
    }

    _.each('keypress,keydown,keyup'.split(','), function(evtype) {
          $(document).bind(evtype, function(e){
              if (e.keyCode == 27) { // Esc
                $('body').attr('style', '');
             }
          });
      });

    $('#age_modal_submit').bind('click', function(){
      document.cookie = "is_Adult=true";
      $('#myModalWelcome').modal('hide').remove();
      $('.modal-backdrop').remove();
      $('body').removeClass('modal-open');
    })

    $('#age_modal_exit').bind('click', function(){
      document.cookie = "is_Adult=false";
      window.location.href = "https://www.google.com/";
    })

  });
})