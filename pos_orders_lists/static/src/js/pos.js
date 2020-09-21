odoo.define('pos_orders_lists.pos_orders_lists', function (require) {
"use strict";

	var module = require('point_of_sale.models');
	var screens = require('point_of_sale.screens');
    var gui = require('point_of_sale.gui');
    var PosPopWidget = require('point_of_sale.popups');
    var core = require('web.core');
    var rpc = require('web.rpc');
    var QWeb = core.qweb;
    var _t = core._t;

	module.load_models({
	    model: 'pos.order',
	    fields: ['id','pos_reference','date_order','partner_id','amount_total','name','session_id'],
	    domain: function(self){ 
	    	if(self.config.allow_load_orders){
		    	var from = moment(new Date()).subtract(self.config.wv_order_date,'d').format('YYYY-MM-DD')+" 00:00:00";
		    	return [['date_order','>',from],['session_id.config_id','in',self.config.wv_lodad_config]]; 
		    }
		    else{
		    	return [['id','=',0]];
		    }
	    },
	    loaded: function(self,old_order){
	    	self.old_order = old_order;
	    },
	});

    var PosOrderPopupWidget = PosPopWidget.extend({
    template: 'PosOrderPopupWidget',
        show: function(options){
            this.options = options || {};
            console.log(options);
            var self = this;
            this._super(options); 
            this.renderElement();
        },
    });

    gui.define_popup({
        'name': 'pos-order-popup', 
        'widget': PosOrderPopupWidget,
    });
    
	var OrderListScreenWidget = screens.ScreenWidget.extend({
	    template: 'OrderListScreenWidget',

	    auto_back: true,
	    renderElement: function() {
	        var self = this;
	        this._super();
	       	this.$('.back').click(function(){
	            self.gui.back();
	        });
	        var search_timeout = null;
	       	this.$('.searchbox input').on('keyup',function(event){
	            var query = this.value;
	            if(query==""){
	            	self.render_list(self.pos.old_order);
	            }
	            else{
	            	self.perform_search(query);
	            }
	        });
	        this.$('.client-list-contents').delegate('.wv_checkout_button','click',function(event){
            	var order_id = $(this).data('id');
            	var order = {}
            	var order_list = self.pos.old_order;
            	for(var i=0;i<order_list.length;i++){
            		if(order_list[i].id == order_id){
            			order = order_list[i];
            		}
            	}
            	rpc.query({
	                model: 'pos.order.line',
	                method: 'search_read',
	                args: [[['order_id','=',$(this).data('id')]],['id','product_id','qty','price_unit','discount','price_subtotal_incl']],
	            }).then(function(order_line){
	        		self.gui.show_popup('pos-order-popup',{'order_line':order_line,'order_id':order_id,'order':order});
		        },function(err,event){
		            event.preventDefault();
		            self.gui.show_popup('error',{
		                'title': _t('Error: Could not Save Changes'),
		                'body': _t('Your Internet connection is probably down.'),
		            });
		        });
		});
	    },
	    show: function(){
	        var self = this;
	        this._super();
	        this.renderElement();
	        this.render_list(self.pos.old_order);
	    },

	    perform_search: function(query){
	    	var old_order = this.pos.old_order;
	    	var results = [];
	        for(var i = 0; i < old_order.length; i++){
	        	var res = this.search_quotations(query, old_order[i]);
	        	if(res != false){
	        	results.push(res);
	        }
	        }
	        this.render_list(results);
	    },
	    search_quotations: function(query,old_order){
	        try {
	            query = query.replace(/[\[\]\(\)\+\*\?\.\-\!\&\^\$\|\~\_\{\}\:\,\\\/]/g,'.');
	            query = query.replace(' ','.+');
	            var re = RegExp("([0-9]+):.*?"+query,"gi");
	        }catch(e){
	            return [];
	        }
	        var results = [];
            var r = re.exec(this._quotations_search_string(old_order));
            if(r){
                var id = Number(r[1]);
                return this.get_quotations_by_id(id);
            }
	        return false;
	    },
	    get_quotations_by_id:function(id){
	    	var old_order = this.pos.old_order;
	    	for(var i=0;i<old_order.length;i++){
	    		if(old_order[i].id == id){
	    			return old_order[i];
	    		}
	    	}
	    },
	    _quotations_search_string: function(old_order){
		        var str =  old_order.pos_reference;
		        if(old_order.partner_id){
		            str += '|' + old_order.partner_id[1];
		        }
		        str = '' + old_order.id + ':' + str.replace(':','') + '\n';
		        return str;
		    },
	    render_list: function(quotationsVal){
	    	var self = this;
	        var contents = this.$el[0].querySelector('.client-list-contents');
	        contents.innerHTML = "";
	        var quotations = quotationsVal;
	        for(var i = 0;i<quotations.length; i++){
	            var quotation    = quotations[i];
                var clientline_html = QWeb.render('WVOrderLine',{widget: self, order:quotation});
                var clientline = document.createElement('tbody');
                clientline.innerHTML = clientline_html;
                clientline = clientline.childNodes[1];
	            contents.appendChild(clientline);
	        }
	    },

	    close: function(){
	        this._super();
	    },
	});
	gui.define_screen({name:'allOrderlist', widget: OrderListScreenWidget});


	var POSOrderListButton = screens.ActionButtonWidget.extend({
        template: 'POSOrderListButton',
        button_click: function(){
        	var self = this;
        	var quotation = this.pos.old_order;
        	var available_qt = []
        	for(var i=0;i<quotation.length;i++){
        		available_qt.push(quotation[i].id)
        	}
	        	var config_id = self.pos.config.id
	        	var from = moment(new Date()).subtract(self.pos.config.wv_order_date,'d').format('YYYY-MM-DD')+" 00:00:00";
				rpc.query({
	                model: 'pos.order',
	                method: 'search_read',
	                args: [[['date_order','>',from],['session_id.config_id','in',self.pos.config.wv_lodad_config],['id','!=',available_qt],['state','!=','done']],['id','name','pos_reference','date_order','partner_id','amount_total','session_id']],
	            }).then(function(order){
						for(var k=0;k<order.length;k++){
							self.pos.old_order.push(order[k]);
						}
    				self.gui.show_screen('allOrderlist',{},'refresh');

			        },function(err,event){
			            event.preventDefault();
			            self.gui.show_popup('error',{
			                'title': _t('Error: Could not Save Changes'),
			                'body': _t('Your Internet connection is probably down.'),
			            });
		      });
        },
    });
	screens.define_action_button({
        'name': 'POS Order List',
        'widget': POSOrderListButton,
        'condition': function(){
            return this.pos.config.allow_load_orders;
        },
    });

  return{
  	PosOrderPopupWidget : PosOrderPopupWidget,
  	OrderListScreenWidget:OrderListScreenWidget,
  };  
});
