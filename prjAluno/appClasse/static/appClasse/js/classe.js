
$(document).ready(()=>{
    function exibirClasse(classe){
        $.get({
          url: "exibirClasse",
          data: {
            classe: classe
          },
          success: (response) => {
              $("#alunosClasse").html(response);  
              
          },
          fail: (response) => {

          }
        })
    }

    function exibirTelaMatricula(classe) {
      $.get({
        url: "telamatricular",
        data: {
          classe: classe
        },
        success: (response) => {
            $("#nomeAluno").off("keyup");
            $("#dadosMatricula").html(response);
            $("#nomeAluno").keyup(()=> sendBuscar());
        
        },
        fail: (response) => {
            alert("Erro na matricula");
        }
      });
    }

    // buscar classe
    function buscarClasse(classe){

        $.get({
            url: "buscarclasse",
            data: {
                classe: classe
            },
            success: (response) => {
                $("#simAtualizar").off("click");
                $("#simDeletar").off("click");
                $("#dadosClasse").html(response);
                  $("#simAtualizar").click( function (){
                    sendAtualizar();
                  });
                  $("#simDeletar").click(function () {
                    sendDeletar();
                    
                  });
            },
            fail: (response) => {},
        });
    }

    function sendDeletar() {
        $.get({
            url: "deletarclasse",
            data: {
                classe: $("#codClasse").val()
            },
            success:(response) => {
                 $("#mensagens").html(response);
                 setTimeout(function () {
                 $("#mensagem").css("display", "none");
                }, 3000);
                sendListar();
            },
            fail: (response) => { $("#mensagens").html(response);}
        });
    }

    function sendAtualizar() {
        $.get({
            url: "atualizarclasse",
            data: {
                ano: $("#anoConfig").val(),
                classe: $("#codClasse").val(),
                serie: $("#serieAtualizar").val(),
                turma: $("#turmaAtualizar").val(),
                periodo: $("#periodoAtualizar").val()
                
            },
            success: (response) => {
                $("#mensagens").html(response);
                 setTimeout(function () {
                 $("#mensagem").css("display", "none");
                }, 3000);
                sendListar();
               
            },
            fail: (response) => {
                $("#mensagens").html(response);
            }
        });
    }
   
    function adicionarNaClasse(aluno) {
        console.log($("#dataMatricula").val());
        $.get({
          url: "adicionarNaClasse",
          data: {
            ano: $("#ano").html(),
            classe: $("#codClasseMatricula").val(),
            aluno: aluno,
            data_matricula: $("#dataMatricula").val()
          },
          success: (response) => {
             $("#mensagensModal").html(response);
            setTimeout(function () {
             $("#mensagemModal").css("display", "none");
            }, 3000);
              
          },
          fail: (response) => {

          }
        });
    }

    function sendGravar() {
        $.get({
        url: "gravarclasse",
        data: {
            ano: $("#anoConfig").val(),
            serie: $("#serie").val(),
            turma: $("#turma").val().toUpperCase(),
            periodo: $("#periodo").val()
        },
        success: (response) => {
            $("#mensagens").html(response);
            setTimeout(function () {
             $("#mensagens").empty();
            }, 3000);
 
            sendListar();
            
             
        },
        fail: (response) => {},
      });
    }

    function sendListar() {

        $.get({
        url: "listarclasse",
        data: {
            ano: localStorage.getItem("anoConfig"),
        },
        success: (response) => {
            $("#corpoTabela").html(response);
            $(".visualizar").off("click");
            $(".atualizar").off("click");
            $(".matricular").off("click");
            $(".visualizar").click(function() {
                  classe = $(this).val();
                   
                  exibirClasse(classe);
            });

             $(".atualizar").click(function (){
                  classe = $(this).val();
              
                  buscarClasse(classe);                               
            });

             $(".matricular").click(function (){
                  classe = $(this).val();
                 
                  exibirTelaMatricula(classe);                               
            });    
        },
        fail: (response) => {

        },
      });
    }

  
   
    $("#gravar").click(()=> {
        sendGravar();
        sendListar();
        limparCampos();
    });

   

    $("#salvarConfig").click(() => {
       
        sendListar();

    });

      $('#configuracoesModal').on('hidden.bs.modal', function (e) {
     
            sendListar();

     });

    function sendBuscar() {
      let nome = document.getElementById("nomeAluno").value;
      let ano = $("#anoConfig").val();
      
      $.get({
        url: "buscarAluno",
        data: {
          nome: nome,
          ano: ano
        },
        success: (response) => {
          
          $("#tabelaAlunos").html(response);
          $(".adicionarNaClasse").off("click");
           $(".adicionarNaClasse").click(function (){
                  aluno = $(this).val();            
                  adicionarNaClasse(aluno); 
                  $(this).addClass("disabled");                                  
            });
        },
      });
    }
  
    sendListar();
   
    function limparCampos() {
           $("#serie").val('');
            $("#turma").val('');
            $("#periodo").val('');
    }


  });