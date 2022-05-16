######################
Componente de opinião
######################

O componente de opinião permite que você faça coletas de opinião em sites e blogs sem
que o seu público perca a experiência de usuário, evitando o redirecionamento para outro
sistema. O seu visitante poderá votar, adicionar novos comentários e visualizar
informações relacionadas aos grupos de opinião formados durante a conversa. O componente possui
duas configurações chave, que são o método de autenticação e o tema visual quer será utilizado.

Autenticação
-------------

Como o visitante não é redirecionado para a EJ mas ainda precisa estar autenticado para participar de uma conversa, o componente oferece três métodos de autenticação.

* **registro por nome e email**: O usuário irá informar um nome e um email para se registrar na EJ. Uma senha será gerada a partir dessas duas informações. A partir do registro, ele segue para a próxima tela e pode então participar.

* **analytics**: O usuário não irá precisar informar nada para participar, mas o gestor do site irá precisar configurar uma *tag* do analytics, para que via cookie este usuário possa ser autenticado na API da EJ. Esse cookie poderá ser utilizado em um segundo momento pelo administrador da conversa, para cruzar dados de opinião com o comportamento do usuário no site, tendo mais pontos de informação sobre o seu público.

* **mautic**: O usuário não irá precisar informar nada para participar, mas o gestor do site irá precisar configurar uma *tag* do mautic, para que via cookie, este usuário possa ser autenticado na API da EJ. Esse cookie poderá ser utilizado em um segundo momento pelo administrador da conversa, para cruzar dados de opinião com dados existentes na instância do mautic que está sendo utilizado.


Temas
-------------

O componente possui quatro temas visuais que podem ter escolhidos na tela de configuração da ferramenta.

.. figure:: ../images/ej-opinion-component-theme.png


Incluíndo o componente em uma pagina
-------------------------------------
Para incluir o componente de opinião em uma página basta copiar o script abaixo e substituir as variáveis pelos valores desejados:

* **host**: `https://www.ejplatform.org` ou outra instancia da EJ.
* **cid**: Identificador da conversa na EJ.
* **theme**: Tema.
* **authenticate-with**: Metodo de autenticação.

.. code-block:: shell

  <meta name="viewport" content="width=device-width, initial-scale=1">
  <script src="https://unpkg.com/ej-conversations@1.9.2/dist/conversations/conversations.esm.js" type="module" ></script>
  <link href="https://fonts.googleapis.com/css?family=Raleway&display=swap" rel="stylesheet">
  <link href="http://localhost:8000/static/css/fontawesome-all.min.css" rel="stylesheet">
  <style>
      /* https://github.com/ionic-team/stencil/issues/2072 */
  @font-face {
  font-family: Folio;
  font-style: normal;
  font-weight: 400;
  src: url(https://unpkg.com/ej-conversations@1.9.1-beta/dist/conversations/assets/fonts/folio_bold_condensed.ttf);
  }

  @font-face {
  font-family: Helvetica;
  font-style: normal;
  font-weight: 400;
    src: url('https://unpkg.com/ej-conversations@1.9.1-beta/dist/conversations/assets/fonts/helvetica_neue_lts_roman.otf');
  }

  @font-face {
  font-family: 'Font Awesome 5 Free';
  font-style: normal;
  font-weight: 400;
    src: url('https://unpkg.com/ej-conversations@1.9.1-beta/dist/conversations/assets/fonts/fa-regular-400.ttf');
  }

  @font-face {
  font-family: 'Font Awesome 5 Free';
  font-style: normal;
  font-weight: 400;
    src: url('https://unpkg.com/ej-conversations@1.9.1-beta/dist/conversations/assets/fonts/fa-brands-400.ttf');
  }

  @font-face {
  font-family: 'Font Awesome 5 Free';
  font-style: normal;
  font-weight: 400;
    src: url('https://unpkg.com/ej-conversations@1.9.1-beta/dist/conversations/assets/fonts/fa-solid-900.ttf');
  }
  </style>

  <ej-conversation host="$HOST" cid="$CONVERSATION_ID" theme="$THEME" authenticate-with="$AUTHENTICATION"></ej-conversation>


O **cid** e o **theme** a serem utilizados podem ser encontrados na url da pagina de coleta via componente de opinião:

.. figure:: ../images/ej-opinion-component-link.png
.. figure:: ../images/ej-opinion-component-link1.png


O atributo ``authenticate-with`` aceita os seguintes valores:

* ``default`` (autenticação por nome e email)
* ``analytics``
* ``mautic``

Caso queria utilizar uma versão diferente ou verificar qual a última versão publicada no npm acesse:
https://www.npmjs.com/package/ej-conversations

Correções de css na pagina do componente
----------------------------------------

O componente fará o melhor possível para carregar bem enquadrado e responsivo, mas é possível que, dependendo de como a pagina foi construída, sejam necessários alguns ajustes no css para que o componente seja apresentado corretamente. Ferramentas como o Divi, muito utilizado no Wordpress para construção de sites, normalmente exigem algumas customizações para não quebrar o componente. Para corrigir as imagens anteriores, por exemplo, o seguinte css foi alterado no tema da página:

.. code-block:: css

  .et_pb_row {
    max-width: unset !important;
    width: unset !important;
    padding: unset !important;
  }
  .et_pb_section {
    padding: unset !important;
  }

  .. _Divi: https://www.elegantthemes.com/gallery/divi/
