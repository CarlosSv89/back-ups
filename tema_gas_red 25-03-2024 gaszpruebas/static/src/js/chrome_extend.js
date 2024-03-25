odoo.define("pos_clients_view.ChromeWidget", function (require) {
  "use strict";

  // require("web.dom_ready");
  const Chrome = require("point_of_sale.Chrome");
  const Registries = require("point_of_sale.Registries");
  const rpc = require("web.rpc");

  const ChromeWidget = (Chrome) =>
    class extends Chrome {
      constructor() {
        super(...arguments);
      }

      get litrosSesion() {
        // Add lt to navbar if data is true
        function innerData(data) {
          if (data >= 0) {
            let dataFormated = data
              .toString()
              .substring(0, data.toString().indexOf(".") + 3);
            const html = `<span>Litros de sesión: ${dataFormated} lt.</span>`;
            $("#litros_totales_container").html(html);
          } else {
            console.error("Error al obtener litros");
          }
        }

        // get lt in async rpc
        async function getLitros(id) {
          try {
            let data = await rpc.query({
              model: "pos.session",
              method: "search_read",
              domain: [["id", "=", id]],
              fields: ["total_lt", "name"],
            });
            innerData(data[0].total_lt);
          } catch (err) {
            console.error(err);
            $("#litros_totales_container").html(`<span>Error litros</span>`);
          }
        }

        // get lt just if session id is loaded
        if (this.env.pos !== undefined) {
          if (this.env.pos.pos_session !== null) {
            getLitros(this.env.pos.pos_session.id);
          } else {
            const html = `<span>Cargando...</span>`;
            $("#litros_totales_container").html(html);
          }
        }
      }
    };

  Registries.Component.extend(Chrome, ChromeWidget);
  return ChromeWidget;
});
