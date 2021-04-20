##############################
Duda: O chatbot oficial da EJ
##############################

Para iniciar a configuração do chatbot, primeiramente é necessário
ter uma instância do Rasa_ rodando. O Rasa é plataforma de inteligência artificial 
utilizada para construir a personalidade do chatbot, e para integrá-lo
a API da EJ. Para instruções técnicas de como rodar o chatbot da EJ em
um ambiente de homologação, acesse https://gitlab.com/pencillabs/ej/ej-bot.


Integrando o chatbot à um webchat genérico
-------------------------------------------

A forma mais rápida de integrar a Duda à um webchat é por meio do projeto rasa-webchat_. 
Este projeto cria um webchat por meio de um script javascript incluído na página html que
se deseja ter o webchat rodando. O seguinte *snippet* pode ser utilizado para integrar o
webchat à Duda.

.. code-block:: html

  <html>
    <head></head>
    <body></body>
    <script>!(function () {
    let e = document.createElement("script"),
      t = document.head || document.getElementsByTagName("head")[0];
    (e.src =
      "https://cdn.jsdelivr.net/npm/rasa-webchat/lib/index.js"),
      (e.async = !0),
      (e.onload = () => {
        window.WebChat.default(
          {
            initPayload: "novo usuario conectado",
            socketUrl: "https://rasaserver.pencillabs.com.br?token=thisismysecret",
          },
          null
        );
      }),
      t.insertBefore(e, t.firstChild);
  })();
  </script>
  </html>

Uma vez integrados, seu público poderá dar opiniões por meio do webchat integrado à instância do Rasa.

.. figure:: ../images/ej-docs-webchat.png 


Integrando o chatbot à uma instância do Rocket.chat
----------------------------------------------------

Caso você queira integrar a Duda à uma instância do Rocket.chat, siga os passos a seguir.


1. Crie no Rocket.chat um usuário com as mesmas credenciais presentes no arquivo `bot/credentials.yml`, no respositório do ejBot;
  * Esse usuário deve ter o papel `bot`, atrelado a sua conta;
  * No `bot/credentials.yml` deve haver uma configuração apontanto para a instância do Rocket.chat;

2. Crie um novo canal, e adicione o usuário bot como participante;

3. Ainda no Rocket, Vá em Administração -> Integrações, e crie uma nova integração de saída (*Outgoing*);
  * No campo url, informe a url da instância do Rasa, por exemplo: https://rasaserver.pencillabs.com.br/webhooks/rocketchat/webhook
  * Preencha os outros campos, de acordo com o nome do canal que foi criado e o nome do usuário bot;

Se tudo foi feito corretamente, agora basta mandar uma mensagem no canal, que a Duda irá responder.

.. figure:: ../images/ej-rasa-rocket.png 

.. _Rasa: https://rasa.com/ 
.. _rasa-webchat: https://github.com/botfront/rasa-webchat


Integrando o chatbot à uma instância de livechat do Rocket.chat
----------------------------------------------------------------

Para utilizar o bot no modo livechat do rocketchat é necessário fazer algumas configurações.

1. Em Ominichannel > Gatilhos de Livechat, crie um novo gatilho:
  * Ative as opções Ativo e Rodar apenas uma vez por visitante;
  * Condition: Tempo de visitante no site;
  * Action - Envie uma mensagem: Escolha a opção "Agente personalizado". Logo abaixo digite o nome do agente do bot no rocketchat. Por fim coloque a mensagem de ` welcome` do bot. Depois clique em salvar.

.. figure:: ../images/ej-rasa-exemplo-gatilho.png

2. Em Webhooks, caso não configurado, configure da seguinte forma:
  * URL do webhook: https://rasaserver.pencillabs.com.br/webhooks/rocketchat/webhook;
  * Token secreto: Insira o token de acesso;
  * Send Request on: Selecione Visitor Messages. Depois clique em salvar.

.. figure:: ../images/ej-rasa-webhook.png

3. Para testar basta ir em Instalação do Livechat copiar o codigo no seu website.

.. figure:: ../images/ej-rasa-livechat-install.png
