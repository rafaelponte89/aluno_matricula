function verificarConfiguracao() {
  if (localStorage.getItem("automatico")) {
    autoPreenchimento.checked = true;
  } else {
    autoPreenchimento.checked = false;
  }
}

function limparStorage() {
  var campos = document.getElementsByClassName("repeticao");
  console.log("limpar"); 
  for(let i=0; i < campos.length; i++) {
    localStorage.removeItem("campo"+i);
    localStorage.removeItem("campoAnt"+i);
  }
  localStorage.removeItem("repeticao");
}
function limparStorage_antiga() {
  localStorage.removeItem("serie");
  localStorage.removeItem("periodo");
  localStorage.removeItem("turma");
  localStorage.removeItem("ano");
  localStorage.removeItem("serieAnt");
  localStorage.removeItem("periodoAnt");
  localStorage.removeItem("turmaAnt");
  localStorage.removeItem("anoAnt");
  localStorage.removeItem("repeticao");
}

//versão 1 estática
function preencherAutomatico2() {
  if (
    localStorage.getItem("repeticao") > 0 &&
    localStorage.getItem("automatico") === "true"
  ) {
    console.log("Serie", localStorage.getItem("serie"));
    $("#serieAtualizar").val(localStorage.getItem("serie"));

    $("#turmaAtualizar").val(localStorage.getItem("turma"));
    $("#periodoAtualizar").val(localStorage.getItem("periodo"));
    $("#anoAtualizar").val(localStorage.getItem("ano"));
    console.log("maior que 2");
  }
}

// Identifica campos a serem repetidos por uma classe
// Nova versão 15012024 dinâmica
function preencherAutomatico() {
  if (
    localStorage.getItem("repeticao") > 0 &&
    localStorage.getItem("automatico") === "true"
  ) {
    var campos = document.getElementsByClassName("repeticao");
    for(var i = 0; i < campos.length; i++ ) {
      campos[i].value = localStorage.getItem("campo"+i);
    }
  }
}

// Identifica campos a serem repetidos por uma classe
// Nova versão 15012024 dinâmica
function verificarRepeticao() {
  if (localStorage.getItem("automatico") === "true") {
    var campos = document.getElementsByClassName("repeticao");
    var verificar = [];
    var temp = [];
    
    if (localStorage.getItem("repeticao")) {

      for (var i =0; i < campos.length; i++) {
        localStorage.setItem("campo"+i, campos[i].value);
        temp.push(localStorage.getItem("campo"+i)); 
      }
      for (var i = 0; i < campos.length; i++) {
        if(localStorage.getItem("campoAnt"+i) === localStorage.getItem("campo"+i)){
          verificar.push(true);
        }
        else {
          verificar.push(false);
        }
        localStorage.setItem("campoAnt"+i, temp[i]);
      }

      var camposCoincidentes = verificar.filter(campo => campo === true);

      if (camposCoincidentes.length === campos.length) {
        console.log(localStorage.getItem("repeticao"));
        var repeticao = parseInt(localStorage.getItem("repeticao"));
        repeticao++;
        localStorage.setItem("repeticao", repeticao);
      } else {
        localStorage.setItem("repeticao", 0);
      }
    } else {
      localStorage.setItem("repeticao", 0);
      for (var i = 0; i < campos.length; i++) {
        localStorage.setItem("campo" + i, campos[i].value);
      }
    }
  } else {

  }
}

//versão 1 estática
function verificarRepeticao2() {
  if (localStorage.getItem("automatico") === "true") {
    if (localStorage.getItem("repeticao")) {
      var serie = localStorage.getItem("serie");
      var turma = localStorage.getItem("turma");
      var periodo = localStorage.getItem("periodo");
      var ano = localStorage.getItem("ano");

      localStorage.setItem("serieAnt", serie);
      localStorage.setItem("turmaAnt", turma);
      localStorage.setItem("periodoAnt", periodo);
      localStorage.setItem("anoAnt", ano);

      var serieAnt = localStorage.getItem("serieAnt");
      var turmaAnt = localStorage.getItem("turmaAnt");
      var periodoAnt = localStorage.getItem("periodoAnt");
      var anoAnt = localStorage.getItem("anoAnt");

      localStorage.setItem("serie", $("#serieAtualizar").val());
      localStorage.setItem("turma", $("#turmaAtualizar").val());
      localStorage.setItem("periodo", $("#periodoAtualizar").val());
      localStorage.setItem("ano", $("#anoAtualizar").val());

      serie = localStorage.getItem("serie");
      turma = localStorage.getItem("turma");
      periodo = localStorage.getItem("periodo");
      ano = localStorage.getItem("ano");

      if (
        serie === serieAnt &&
        turma === turmaAnt &&
        periodo === periodoAnt &&
        ano === anoAnt
      ) {
        console.log(localStorage.getItem("repeticao"));
        var repeticao = parseInt(localStorage.getItem("repeticao"));
        repeticao++;
        localStorage.setItem("repeticao", repeticao);
      } else {
        localStorage.setItem("repeticao", 0);
      }
    } else {
      localStorage.setItem("repeticao", 0);
      localStorage.setItem("serie", $("#serieAtualizar").val());
      localStorage.setItem("turma", $("#turmaAtualizar").val());
      localStorage.setItem("periodo", $("#periodoAtualizar").val());
      localStorage.setItem("ano", $("#anoAtualizar").val());
    }
  }
}

var salvarConfig = document.getElementById("salvarConfig");
var autoPreenchimento = document.getElementById("preenchimentoAutomatico");

salvarConfig.addEventListener("click", function () {
  if (autoPreenchimento.checked) {console.log("automatico");
    localStorage.setItem("automatico", true);
    
  } else {
    localStorage.removeItem("automatico");
   
    limparStorage();
  }
});
verificarConfiguracao();
