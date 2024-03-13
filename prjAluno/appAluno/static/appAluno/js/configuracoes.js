
function verificarConfiguracao() {
 
  //Carregar seleção versão
  if(localStorage.getItem("completa")){
    //$("#topo").show();
    $("#menu").show();
    $("#versaoCompleta").prop("checked",true);
  }
  else {
    //$("#topo").hide();
    $("#menu").hide();
    $("#versaoCompleta").prop("checked",false);
  }

  //Carregar preenchimento automatico
  if (localStorage.getItem("automatico")) {
    autoPreenchimento.checked = true;
  } else {
    autoPreenchimento.checked = false;
  }

  //Carregar ano Configuração
  if (localStorage.getItem("anoConfig")) { 
    document.getElementById("ano").innerHTML = localStorage.getItem("anoConfig");
    document.getElementById("anoConfig").value = localStorage.getItem("anoConfig");
  }
  else {
    const date = new Date();
    const currentYear = date.getFullYear();
    localStorage.setItem("anoConfig",currentYear);
    document.getElementById("ano").innerHTML = localStorage.getItem("anoConfig");
    document.getElementById("anoConfig").value = localStorage.getItem("anoConfig");
  }
}

function limparStorage() {
  var campos = document.getElementsByClassName("repeticao");
  console.log("limpar"); 
  for(let i=0; i < campos.length; i++) {
    localStorage.removeItem("campo"+i);
    localStorage.removeItem("campoAnt"+i);
    console.log(i);
  }
  localStorage.removeItem("repeticao");
}

function selecionarVersao() {
  $("#salvarConfig").click(() => {
      if($("#versaoCompleta").prop("checked") == true) {
        localStorage.setItem("completa",true);
      }
      else {
        localStorage.removeItem("completa");
      }
  });

  $('#configuracoesModal').on('hidden.bs.modal', function (e) {
    if($("#versaoCompleta").prop("checked") == true) {
      localStorage.setItem("completa",true);
    }
    else {
      localStorage.removeItem("completa");
    }

  });


}
selecionarVersao();
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

// Identifica campos a serem repetidos através da  classe
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

var salvarConfig = document.getElementById("salvarConfig");
var autoPreenchimento = document.getElementById("preenchimentoAutomatico");
var anoConfig = document.getElementById("anoConfig");

//quando clica no botão salvar de configuração
salvarConfig.addEventListener("click", function () {
  setarConfigAno();
 
  
});

$('#configuracoesModal').on('hidden.bs.modal', function (e) {
  setarConfigAno();

});


function setarConfigAno() {
  if (localStorage.getItem("anoConfig")) { 
   
    if ($("#anoConfig").val() !== ''){

      localStorage.setItem("anoConfig",$("#anoConfig").val());
      document.getElementById("ano").innerHTML = localStorage.getItem("anoConfig");
      document.getElementById("anoConfig").value = localStorage.getItem("anoConfig");
      
    }
    else {
      const date = new Date();
    const currentYear = date.getFullYear();
    localStorage.setItem("anoConfig",currentYear);
    document.getElementById("ano").innerHTML = localStorage.getItem("anoConfig");
    document.getElementById("anoConfig").value = localStorage.getItem("anoConfig");
    }
  }
  else {
    const date = new Date();
    const currentYear = date.getFullYear();
    localStorage.setItem("anoConfig",currentYear);
    document.getElementById("ano").innerHTML = localStorage.getItem("anoConfig");
    document.getElementById("anoConfig").value = localStorage.getItem("anoConfig");
  }
}

verificarConfiguracao();
