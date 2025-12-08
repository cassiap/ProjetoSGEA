// === Máscara de telefone: (XX) XXXXX-XXXX ===
function aplicarMascaraTelefone(input) {
  input.addEventListener("input", function () {
    let valor = input.value.replace(/\D/g, ""); // só números

    if (valor.length > 11) valor = valor.slice(0, 11);

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

  // ---- Datepicker / Timepicker----
  var temJQ = typeof window.$ !== "undefined";
  var temDatepicker = temJQ && typeof $.fn.datepicker !== "undefined";
  var temTimepicker = temJQ && typeof $.fn.timepicker !== "undefined";

  // Locale pt-BR para datepicker, se disponível
  if (temDatepicker && $.datepicker) {
    $.datepicker.regional["pt-BR"] = {
      closeText: "Fechar",
      prevText: "&#x3C;Anterior",
      nextText: "Próximo&#x3E;",
      currentText: "Hoje",
      monthNames: ["Janeiro","Fevereiro","Março","Abril","Maio","Junho","Julho","Agosto","Setembro","Outubro","Novembro","Dezembro"],
      monthNamesShort: ["Jan","Fev","Mar","Abr","Mai","Jun","Jul","Ago","Set","Out","Nov","Dez"],
      dayNames: ["Domingo","Segunda-feira","Terça-feira","Quarta-feira","Quinta-feira","Sexta-feira","Sábado"],
      dayNamesShort: ["Dom","Seg","Ter","Qua","Qui","Sex","Sáb"],
      dayNamesMin: ["Dom","Seg","Ter","Qua","Qui","Sex","Sáb"],
      weekHeader: "Sm",
      dateFormat: "yy-mm-dd",
      firstDay: 0,
      isRTL: false,
      showMonthAfterYear: false,
      yearSuffix: ""
    };
    $.datepicker.setDefaults($.datepicker.regional["pt-BR"]);
  }

  // Datepicker para campos de data
  if (temDatepicker) {
    // data_inicio: hoje para frente
    $(".datepicker#id_data_inicio, input[name='data_inicio'].datepicker").datepicker({
      minDate: 0, // impede passado
      changeMonth: true,
      changeYear: true,
      dateFormat: "yy-mm-dd"
    });

    // data_fim: sincroniza para nunca ser antes do início
    var $inicio = $(".datepicker#id_data_inicio, input[name='data_inicio'].datepicker");
    var $fim = $(".datepicker#id_data_fim, input[name='data_fim'].datepicker").datepicker({
      changeMonth: true,
      changeYear: true,
      dateFormat: "yy-mm-dd"
    });

    $inicio.on("change", function () {
      var val = $(this).datepicker("getDate");
      if (val) {
        $fim.datepicker("option", "minDate", val);
        var fimAtual = $fim.datepicker("getDate");
        if (fimAtual && fimAtual < val) {
          $fim.datepicker("setDate", val);
        }
      }
    });
  }

  // Timepicker para campos de horário
  if (temTimepicker) {
    $(".timepicker, #id_horario.timepicker").timepicker({
      timeFormat: "HH:mm",
      hourGrid: 4,
      minuteGrid: 10
    });
  }
});
