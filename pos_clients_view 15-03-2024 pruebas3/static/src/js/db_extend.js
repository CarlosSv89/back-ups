odoo.define("pos_clients_view.DB", function (require) {
  "use strict";

  var PosDB = require("point_of_sale.DB");

  // trying to add more fields to the search string
  PosDB.DB = PosDB.include({
    _partner_search_string: function (partner) {
      var str = partner.name || "";
      if (partner.barcode) {
        str += "|" + partner.barcode;
      }
      if (partner.address) {
        str += "|" + partner.address;
      }
      if (partner.phone) {
        str += "|" + partner.phone.split(" ").join("");
      }
      if (partner.mobile) {
        str += "|" + partner.mobile.split(" ").join("");
      }
      if (partner.email) {
        str += "|" + partner.email;
      }
      if (partner.id_cliente) {
        str += "|" + partner.id_cliente;
      }
      if (partner.id) {
        str += "|" + partner.id;
      }
      str =
        "" + partner.id + ":" + str.replace(":", "").replace(/\n/g, " ") + "\n";
      return str;
    },
  });
});
