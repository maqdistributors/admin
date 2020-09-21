odoo.define('maqabim.pos', function (require) {
"use strict";

var models = require('point_of_sale.models');
var screens = require('point_of_sale.screens');
var core = require('web.core');
var session = require('web.session');

var QWeb = core.qweb;



models.load_fields('account.tax','tax_group_id');

var _super_order = models.Order.prototype;

var pmodels = models.PosModel.prototype.models;
for (var i = 0; i < pmodels.length; i++) {
    var model = pmodels[i];
    if (model.label === 'pictures') {
        model.loaded = function(self) {
            self.company_logo = new Image();
            var logo_loaded = new $.Deferred();
            self.company_logo.onload = function() {
                var img = self.company_logo;
                var ratio = 1;
                var targetwidth = 300;
                var maxheight = 150;
                if (img.width !== targetwidth) {
                    ratio = targetwidth / img.width;
                }
                if (img.height * ratio > maxheight) {
                    ratio = maxheight / img.height;
                }
                var width = Math.floor(img.width * ratio);
                var height = Math.floor(img.height * ratio);
                var c = document.createElement('canvas');
                c.width = width;
                c.height = height;
                var ctx = c.getContext('2d');
                ctx.drawImage(self.company_logo, 0, 0, width, height);

                self.company_logo_base64 = c.toDataURL();
                logo_loaded.resolve();
            };
            self.company_logo.onerror = function() {
                logo_loaded.reject();
            };
            //crossOrigin attribute clear the session information on safari browser, hence we are not getting an image of current user's company,
            //instead it alwasy return the admin user's company logo, so to get the correct company logo, we pass the company through query string, to get extact logo of the current pos company
            self.company_logo.crossOrigin = "anonymous";
            self.company_logo.src = '/web/binary/company_logo' + '?dbname=' + session.db + '&company=' + self.company.id + '&_' + Math.random();
            return logo_loaded;
        }
        break;
    }
}

models.Order = models.Order.extend({

    export_for_printing: function() {
        var json = _super_order.export_for_printing.apply(this, arguments);
        json.tax_details = this.get_tax_details_by_tax_group();
        return json;
    },

    get_tax_details_by_tax_group: function() {
        var fulldetails = [];

        this.orderlines.each(function(line) {
            var ldetails = line.get_tax_details_by_group();
            for (var id in ldetails) {
                if (ldetails.hasOwnProperty(id)) {
                    var details = _.findWhere(fulldetails, {
                        id: id
                    });
                    if (details) {
                        details['amount'] += ldetails[id]['amount'];
                    } else {
                        fulldetails.push({
                            amount: ldetails[id]['amount'],
                            name: ldetails[id]['name'],
                            id: id,
                        });
                    }
                }
            }
        });
        return _.sortBy(fulldetails, 'amount');
    },
});
var _super_orderline = models.Orderline.prototype;

models.Orderline = models.Orderline.extend({
    get_tax_details_by_group: function(){
        return this.get_all_prices().taxByGroup;
    },
    _map_tax_fiscal_position_custom: function(tax) {
        /*
            This method will return the multiple taxes if same tax is replace by multiple taxes on fiscalposition
            retrun Array if more than one tax found else return orignal tax

            TODO: for included price this won't work
        */
        var self = this;
        var current_order = this.pos.get_order();
        var order_fiscal_position = current_order && current_order.fiscal_position;
        var taxes = [];
        if (order_fiscal_position) {
            _.each(order_fiscal_position.fiscal_position_taxes_by_id, function(t) {
                if (t.tax_src_id[0] === tax.id) {
                    taxes.push(self.pos.taxes_by_id[t.tax_dest_id[0]]);
                }
            });
        }
        if (taxes.length > 1) {
            return taxes;
        }

        return tax;
    },
    compute_all: function(taxes, price_unit, quantity, currency_rounding, no_map_tax) {
        /*
            Inherited in order to support the fiscal position having tax which replace with
            multiple taxes
            i.e GST 5% Replace with GST FOR SALE 3% AND PST FOR SALE 2%
        */
        var self = this;
        _.each(taxes, function(tax, i) {
            if (!no_map_tax) {
                var temp_tax = tax;
                tax = self._map_tax_fiscal_position_custom(tax);
                if (tax != temp_tax) {
                    Array.prototype.push.apply(taxes, tax);
                    taxes[i] = false;
                }
            }
        });
        return _super_orderline.compute_all.call(this, taxes, price_unit, quantity, currency_rounding, no_map_tax);
    },
    get_all_prices: function() {
        /*
            complete override to group the taxes by tax group
            changes are marked with CUSTOM
        */
        var self = this;
        var price_unit = this.get_unit_price() * (1.0 - (this.get_discount() / 100.0));
        var taxtotal = 0;

        var product =  this.get_product();
        var taxes_ids = product.taxes_id;
        var taxes =  this.pos.taxes;
        var taxdetail = {};
        var product_taxes = [];

        _(taxes_ids).each(function(el){
            product_taxes.push(_.detect(taxes, function(t){
                return t.id === el;
            }));
        });

        var all_taxes = this.compute_all(product_taxes, price_unit, this.get_quantity(), this.pos.currency.rounding);
        var tax_by_group = {};

        _(all_taxes.taxes).each(function(tax) {
            taxtotal += tax.amount;
            taxdetail[tax.id] = tax.amount;

            //CUSTOM CODE START
            var tax_obj = self.pos.taxes_by_id[tax.id];
            var group_id = tax_obj.tax_group_id[0];
            if (!_.has(tax_by_group), group_id) {
                tax_by_group[group_id] = {amount: tax.amount, name: tax_obj.tax_group_id[1]};
            } else {
                tax_by_group[group_id]['amount'] += tax.amount;
            }
             //CUSTOM CODE END
        });

        return {
            "priceWithTax": all_taxes.total_included,
            "priceWithoutTax": all_taxes.total_excluded,
            "tax": taxtotal,
            "taxDetails": taxdetail,
            "taxByGroup": tax_by_group, //custom
        };
    },
    generate_wrapped_product_name: function() {
        /*
            complete override to append the internal reference on xml receipt, a receipt that print via posbox
            changes are marked with CUSTOM
        */
        var MAX_LENGTH = 24; // 40 * line ratio of .6
        var wrapped = [];
        //CUSTOM START
        var name = '';
        if (this.get_product().default_code)
            name += '[' + this.get_product().default_code + ']'
        name = name + this.get_product().display_name;
        //CUSTOM END
        var current_line = "";
        while (name.length > 0) {
            var space_index = name.indexOf(" ");

            if (space_index === -1) {
                space_index = name.length;
            }

            if (current_line.length + space_index > MAX_LENGTH) {
                if (current_line.length) {
                    wrapped.push(current_line);
                }
                current_line = "";
            }

            current_line += name.slice(0, space_index + 1);
            name = name.slice(space_index + 1);
        }

        if (current_line.length) {
            wrapped.push(current_line);
        }
        return wrapped;
    },
});

screens.OrderWidget.include({
    update_summary: function() {
        /*
            Override to display the subtotal and taxes by group
        */
        var order = this.pos.get_order();
        if (!order.get_orderlines().length) {
            return;
        }

        var subtotal = order ? order.get_total_without_tax() : 0;
        var total     = order ? order.get_total_with_tax() : 0;
        var taxes     = order ? total - subtotal : 0;

        var $tax_details = $(QWeb.render('TaxGroup', {widget: this}));

        this.el.querySelector('.summary .total > .value').textContent = this.format_currency(total);
        $tax_details.appendTo($(this.el.querySelector('.summary .total .subentry')).empty());
        this.el.querySelector('.summary .total .subtotal .value').textContent = this.format_currency(subtotal);
    },
});


});