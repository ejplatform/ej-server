###############
Getting Started
###############

.. contents::
   :depth: 2

Desenvolvimento local (Docker)
------------------------------

Primeiro, clone o repositório:

.. code-block:: shell

    $ git clone https://gitlab.com/pencillabs/ej/ej-server
    $ cd ej-server

É recomendado executar a EJ com o Docker. Com ele, você pode rapidamente
iniciar o servidor de desenvolvimento com os seguintes comandos:

.. code-block:: shell

    $ sudo pip3 install invoke==1.4.1 --user
    $ inv docker-up
    $ inv docker-logs

Isso servirá a aplicação utilizando o arquivo **docker/docker-compose.yml**.
Toda mudança realizada nesse repositório será refletida dentro do container `server`.

Você pode acessar a instância que estará rodando em `http://localhost:8000`.

Para reconstruir a imagem do servidor, você pode rodar  `inv docker-build --no-cache`.

Alguns comandos úteis para tasks de desenvolvimento:

==================  ============================================= 
Comando             Descrição  
==================  =============================================
inv docker-up       Cria os containers e roda a aplicação
inv db-fake         Cria dados fictícios para o ambiente de desenvolvimento
inv sass            Compila e serve os arquivos estáticos alterados (arquivos sass)
inv docker-logs     Exibe os logs do django 
inv docker-stop     Para os containers
inv docker-rm       Remove os containers
inv docker-attach   Realiza conexão ao container do ej-server
==================  =============================================

Documentação
-------------

Para atualizar a documentação, onde está a página atual, execute:

.. code-block:: shell

    $ inv docker-exec "inv docs"
    
As mudanças estarão disponíveis no diretório ``build/docs/``.


Mudando o tema
--------------

Os comandos mostrados anteriormente constrõem a EJ utilizando o tema padrão. A EJ aceita temas adicionais
e já vem com o tema pré instalado "cpa". Os passos para reconstruir os conteúdos estáticos são:

.. code-block:: shell

    $ inv docker-exec "inv js db-assets"
    $ inv docker-exec "inv sass -t cpa" 

Depois é necessário rodar o servidor com a flag de tema:

.. code-block:: shell

    $ inv docker-exec "inv run -t cpa"

Testes
------

É importante executar testes com frequência, na EJ é utilizado o pytest:

.. code-block:: shell

    $ inv docker-test

Docker bash
-----------

You probably will want to execute commands inside the container.
It is possible to open a bash shell in the main "web" container with::

.. code-block:: shell

    $ inv docker-attach

You also can execute commands without open docker bash shell::

.. code-block:: shell

    $ inv docker-exec "command"
