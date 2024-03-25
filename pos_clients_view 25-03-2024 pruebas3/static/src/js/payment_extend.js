// odoo.define("pos_clients_view.PaymentScreen", function (require) {
//   "use strict";

//   var PaymentScreen = require("point_of_sale.PaymentScreen");

//   async function validateOrder(isForceValidate) {
//     var text = document.getElementById("order_folio").value;
//     console.log("Folio: ", text);
//     if (text === "") {
//       console.log("Falta la referencia del pedido :", text);
//       this.showPopup("ErrorPopup", {
//         title: this.env._t("Falta la referencia del pedido"),
//         body: this.env._t(
//           "Por favor, ingrese la referencia del pedido antes de validar."
//         ),
//       });
//       return;
//     } else {
//       if (this.env.pos.config.cash_rounding) {
//         if (!this.env.pos.get_order().check_paymentlines_rounding()) {
//           this.showPopup("ErrorPopup", {
//             title: this.env._t("Rounding error in payment lines"),
//             body: this.env._t(
//               "The amount of your payment lines must be rounded to validate the transaction."
//             ),
//           });
//           return;
//         }
//       }
//       if (await this._isOrderValid(isForceValidate)) {
//         // remove pending payments before finalizing the validation
//         for (let line of this.paymentLines) {
//           if (!line.is_done()) this.currentOrder.remove_paymentline(line);
//         }
//         await this._finalizeValidation();
//       }
//     }
//   }

//   PaymentScreen.prototype.validateOrder = validateOrder;

//   return PaymentScreen;
// });
