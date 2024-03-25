odoo.define("pos_clients_view.Models", function (require) {
  "use strict";
  var models = require("point_of_sale.models");

  // ------------------------- Docs -----------------------------
  // Add fields to the list of read fields when a model is loaded
  // by the point of sale.
  // e.g: module.load_fields("product.product",['price','category'])

  // exports.load_fields = function(model_name, fields) {
  //   if (!(fields instanceof Array)) {
  //       fields = [fields];
  //   }

  //   var models = exports.PosModel.prototype.models;
  //   for (var i = 0; i < models.length; i++) {
  //       var model = models[i];
  //       if (model.model === model_name) {
  // if 'fields' is empty all fields are loaded, so we do not need
  // to modify the array
  //           if ((model.fields instanceof Array) && model.fields.length > 0) {
  //               model.fields = model.fields.concat(fields || []);
  //           }
  //       }
  //   }
  // };

  // Adding the id_cliente field to the res.partner model, because it is not loaded by default
  models.load_fields("res.partner", ["id_cliente"]);
});
