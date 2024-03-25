odoo.define('experts_pos_extend.PricelistBtn', function (require) {
    "use strict";
        const { useListener } = require('web.custom_hooks');
        const SetPricelistButton = require('point_of_sale.SetPricelistButton');
        const Registries = require('point_of_sale.Registries');
        const session = require('web.session');
    
        const SetPricelistButtonExt = (SetPricelistButton) =>
            class extends SetPricelistButton {
                constructor() {
                    session.user_has_group('experts_pos_extend.view_pricelist_menu_pos').then(function (has_group) {
                        if (has_group){
                            $('.o_pricelist_button').removeClass('oe_hidden');
                        }else{
                            $('.o_pricelist_button').addClass('oe_hidden');
                        }
                    });
                    super(...arguments);
                    useListener('click', this.onClick);
                }
            };
        Registries.Component.extend(SetPricelistButton, SetPricelistButtonExt);
        return SetPricelistButton;
    
    });