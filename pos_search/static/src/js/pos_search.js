odoo.define('pos_search.pos_search', function (require) {
"use strict";
    
    var core = require('web.core');
    var screens = require('point_of_sale.screens');
    var PosDB = require('point_of_sale.DB');

    var QWeb = core.qweb;
    var _t = core._t;

    PosDB.include({
        init: function(options){
            var self = this;
            this._super(options);
            this.name_search_in_string = {};
            this.internal_reference_search_in_string = {};
            this.category_search_in_string = {};
            this.barcode_search_in_string = {};
        },
        _product_name_search_in_string: function(product){
            if (!product.display_name){
                return '';
            }
            var str = product.display_name;
            str  = product.id + ':' + str.replace(/:/g,'') + '\n';
            return str;
        },
        _product_internal_reference_search_in_string: function(product){
            if (!product.default_code){
                return '';
            }
            var str = product.default_code;
            str  = product.id + ':' + str.replace(/:/g,'') + '\n';
            return str;
        },
        _product_category_search_in_string: function(product){
            if (!product.pos_categ_id){
                return '';
            }
            var str = product.pos_categ_id[1];
            str  = product.id + ':' + str.replace(/:/g,'') + '\n';
            return str;
        },
        _product_barcode_search_in_string: function(product){
            if (!product.barcode){
                return '';
            }
            var str = product.barcode;
            str  = product.id + ':' + str.replace(/:/g,'') + '\n';
            return str;
        },
        add_products: function(products){
            this._super(products);
            if(!products instanceof Array){
                products = [products];
            }
            for(var i = 0, len = products.length; i < len; i++){
                var product = products[i];
                // FOR NAME SEARCH
                if(this.name_search_in_string === undefined){
                    this.name_search_in_string = '';
                }
                this.name_search_in_string += this._product_name_search_in_string(product);

                // FOR INTERNAL REFERENCE SEARCH
                if(this.internal_reference_search_in_string === undefined){
                    this.internal_reference_search_in_string = '';
                }
                this.internal_reference_search_in_string += this._product_internal_reference_search_in_string(product);

                // FOR CATEGORY SEARCH
                if(this.category_search_in_string === undefined){
                    this.category_search_in_string = '';
                }
                this.category_search_in_string += this._product_category_search_in_string(product);

                // FOR BARCODE SEARCH
                if(this.barcode_search_in_string === undefined){
                    this.barcode_search_in_string = '';
                }
                this.barcode_search_in_string += this._product_barcode_search_in_string(product);
            }
        },
        search_product_in_search_in:function(search_in, query){
            try {
                query = query.replace(/[\[\]\(\)\+\*\?\.\-\!\&\^\$\|\~\_\{\}\:\,\\\/]/g,'.');
                query = query.replace(/ /g,'.+');
                var re = RegExp("([0-9]+):.*?"+query,"gi");
            }catch(e){
                return [];
            }
            var results = [];
            for(var i = 0; i < this.limit; i++){
                if (search_in == 'name'){
                    var r = re.exec(this.name_search_in_string);
                } else if(search_in == 'category'){
                    var r = re.exec(this.category_search_in_string);
                } else if(search_in == 'barcode'){
                    var r = re.exec(this.barcode_search_in_string);
                } else {
                    var r = re.exec(this.internal_reference_search_in_string);
                }

                if(r){
                    var id = Number(r[1]);
                    results.push(this.get_product_by_id(id));
                }else{
                    break;
                }
            }
            return results;
        }
    });

    screens.ProductCategoriesWidget.include({
        init: function(parent, options){
        	var self = this;
            this._super(parent, options);
            this.search_in_handler = function(event){
                self.seach_in(this.value);
                self.clear_search();
            };
        },
        renderElement: function(){
            this._super();
            this.el.querySelector('.search_in').addEventListener('change', this.search_in_handler);
        },
        seach_in : function(search_in){
            var db = this.pos.db;
            if(!search_in){
                this.search_in = 'name';
            }else{
                this.search_in = search_in;
            }
        },
        perform_search: function(category, query, buy_result){
            var self = this;
            var products;
            if(query){
                products = this.pos.db.search_product_in_search_in(this.search_in, query);
                if(buy_result && products.length === 1){
                        this.pos.get_order().add_product(products[0]);
                        this.clear_search();
                }else{
                    this.product_list_widget.set_product_list(products);
                }
            }else{
                this._super(category, query, buy_result)
            }
        },
    });

});
