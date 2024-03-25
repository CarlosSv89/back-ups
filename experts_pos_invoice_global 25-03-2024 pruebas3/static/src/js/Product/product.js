odoo.define('experts_pos_extend.Product', function (require) {
"use strict";
    // Add fields and inherit methods from Products
    const models = require('point_of_sale.models');

    models.Orderline = models.Orderline.extend({
        get_full_product_name:function () {
            // Get full name for each line
            var self = this;
            var name = this.product.display_name;
            var default_code = this.product.default_code
            var prod_desc = self.pos.config.print_product_description
            var full_name = `[${default_code}] ${name}`
            if(prod_desc == 'code'){
                full_name = `[${default_code}]`
            }else if(prod_desc == 'code'){
                full_name = `${name}`
            }

            if (this.description) {
                full_name += ` (${this.description})`;
            }
            return full_name;
        }
    })

});