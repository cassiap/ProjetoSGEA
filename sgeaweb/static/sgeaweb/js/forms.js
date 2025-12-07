// sgeaweb/static/sgeaweb/js/forms.js

// === Máscara de telefone: (XX) XXXXX-XXXX ===
function aplicarMascaraTelefone(input) {
  input.addEventListener("input", function () {
    let valor = input.value.replace(/\D/g, ""); // só números

    if (valor.length > 11) {
      valor = valor.slice(0, 11);
    }

    if (valor.length > 6) {
      input.value = `(${valor.slice(0, 2)}) ${valor.slice(2, 7)}-${valor.slice(7)}`;
    } else if (valor.length > 2) {
      input.value = `(${valor.slice(0, 2)}) ${valor.slice(2)}`;
    } else if (valor.length > 0) {
      input.value = `(${valor}`;
    } else {
      input.value = "";
    }
  });
}

document.addEventListener("DOMContentLoaded", function () {
  // Máscara de telefone
  document.querySelectorAll(".telefone-mask").forEach(function (input) {
    aplicarMascaraTelefone(input);
  });

  // Datepicker jQuery UI para campos de data
  if (typeof $ !== "undefined" && typeof $.fn.datepicker !== "undefined") {
    $(".datepicker").datepicker({
      dateFormat: "yy-mm-dd",
      changeMonth: true,
      changeYear: true
    });
  }

  // Timepicker jQuery UI Addon para campos de horário
  if (typeof $ !== "undefined" && typeof $.fn.timepicker !== "undefined") {
    $(".timepicker").timepicker({
      timeFormat: "HH:mm",
      hourGrid: 4,
      minuteGrid: 10
    });
  }
});
