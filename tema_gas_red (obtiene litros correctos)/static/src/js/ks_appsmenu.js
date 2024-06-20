odoo.define("tema_gas_red.appsmenu", function(require) {
    "use strict";

    var AppsMenu = require("web.AppsMenu");
    var session = require("web.session");
    var config = require("web.config");
    var core = require("web.core");
    var QWeb = core.qweb;

    function ks_GetReducedMenuData(memo, menu) {
        if (menu.action) {
            var key = menu.parent_id ? menu.parent_id[1] + "/" : "";
            menu["ks_title"] = (key + menu.name).toLowerCase();
            memo[key + menu.name] = menu;
        }
        if (menu.children.length) {
            _.reduce(menu.children, ks_GetReducedMenuData, memo);
        }
        return memo;
    }

    AppsMenu.include({
        // FixMe: Bootstrap events not working
        // events: _.extend({}, AppsMenu.prototype.events, {
        //     "keydown .ks_menu_search_box input": "_ksSearchValuesMovement",
        //     "input .ks_menu_search_box input": "_ksSearchMenuListTime",
        //     "click .ks-menu-search-value": "_ksSearchValuesSelecter",

        //     "shown.bs.dropdown": "_ksSearchFocus",
        //     "hidden.bs.dropdown": "_ksSearchResetvalues",
        //     "hide.bs.dropdown": "_ksHideAppsMenuList",
        //     "click .ks_rmv_fav": "_ksRemoveFavApps",
        //     "click .ks_add_fav": "_ksAddFavApps",
        //     "click .ks_close_app_drawer": "_ksHideFavIcons",
        // }),
        /**
         * @overrideks_appsmenu_active
         * @param {web.Widget} parent
         * @param {Object} menuData
         * @param {Object[]} menuData.children
         */
        init: function(parent, menuData) {
            this._super.apply(this, arguments);
            for (let i in this._apps) {
                this._apps[i].web_icon_data = menuData.children[i].web_icon_data;
            }
            var today = new Date();
            var curHr = today.getHours();
            var message = "Hi, ";
            if (curHr < 12) {
                message = "Good Morning, ";
            } else if (curHr < 18) {
                message = "Good Afternoon, ";
            } else {
                message = "Good Evening, ";
            }
            this.ks_user_id = session.uid;
            this.ks_user_name = message + session.name;
            this._ks_fuzzysearchableMenus = _.reduce(
                menuData.children,
                ks_GetReducedMenuData, {}
            );

            this.ks_fav_apps = [];
        },
        /**
         * @override
         **/
//         
    });
});