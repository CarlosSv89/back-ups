odoo.define('experts_pos_extend.Order', function (require) {
    "use strict";
    // Prevent sale without stock
    const models = require('point_of_sale.models');
    const utils = require('web.utils');
    const session = require('web.session');
    const field_utils = require('web.field_utils');
    const round_pr = utils.round_precision;

    var _super_order = models.Order.prototype;
    models.Order = models.Order.extend({
        add_product: function(product, options){
            var self = this;
            if (product.type === "service"){
                return _super_order.add_product.call(this, product, options);
            }else{
            if (self.pos.config.allow_sale_product_without_stock) {
                return _super_order.add_product.call(self, product, options);
            }
            if(product.qty_available <= 0.0){
                alert('El producto no puede ser agregado porque no tiene cantidad disponible !');
                return ;
            } else {
                return _super_order.add_product.call(self, product, options);
            }
            }
        },
    });

    var _super_orderline = models.Orderline.prototype;
    models.Orderline = models.Orderline.extend({
        set_quantity: function(quantity, keep_price){
            this.order.assert_editable();
            console.log("config: ",this.pos.config)
            if (this.pos.config.allow_sale_product_without_stock) {
                return _super_orderline.set_quantity.call(this, quantity, keep_price);
            }
            if(quantity === 'remove'){
                this.order.remove_orderline(this);
                return;
            }else{
                var quant = parseFloat(quantity) || 0;
                var unit = this.get_unit();
                var available = this.product.qty_available
                if(unit){
                    if (unit.rounding) {
                        var decimals = this.pos.dp['Product Unit of Measure'];
                        var rounding = Math.max(unit.rounding, Math.pow(10, -decimals));
                        if ( round_pr(quant, rounding) > available){
                            alert('El producto no puede ser agregado porque no tiene cantidad disponible !');
                            return ;
                        }else{
                            this.quantity    = round_pr(quant, rounding);
                            this.quantityStr = field_utils.format.float(this.quantity, {digits: [69, decimals]});
                        }
                    } else {
                        if ( round_pr(quant, 1) > available){
                            alert('El producto no puede ser agregado porque no tiene cantidad disponible !');
                            return ;
                        }else{
                            this.quantity    = round_pr(quant, 1);
                            this.quantityStr = this.quantity.toFixed(0);
                        }
                    }
                }else{
                    if ( quant > available){
                        alert('El producto no puede ser agregado porque no tiene cantidad disponible !');
                        return ;
                    }else{
                        this.quantity    = quant;
                        this.quantityStr = '' + this.quantity;
                    }
                }
            }
            
            if(! keep_price && ! this.price_manually_set){
                this.set_unit_price(this.product.get_price(this.order.pricelist, this.get_quantity()));
                this.order.fix_tax_included_price(this);
            }
            this.trigger('change', this);
        },
    });
});