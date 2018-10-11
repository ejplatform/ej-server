Adicionar funcionalidades no ej-server
======================================

Para cada issue a ser resolvida, seguir o seguinte procedimento:

- Caso seu ambiente de desenvolvimento ainda não esteja preparado,
  então clone o repositório, prepare ele conforme é explicado no
  `README.rst`_ e instale os hooks para checar seu código com::

    $ inv install-hooks

- Mude a branch local para ``dev`` ou qualquer outra que queira criar
  para resolver sua issue específica. E.g.::

    $ git checkout dev

- Sempre rode os testes antes de fazer qualquer commit (rode mesmo
  porque seu PR não será aceito se seus testes não estiverem passando!)::

    $ inv test

- Ao terminar sua issue, para enviar para a branch MASTER, abra um
  ticket de pull request no github com o sentido (base <- head)::

    ejplatform/ej-server/master <- ejplatform/ej-server/dev

- Espere o Travis CI, GitLab CI e o Code Climate executar os testes de
  integração
- Se os testes passarem, você ou outro contribuidor estarão livres para
  aceitar seu PR :rocket:
- Se a branch que criou não for a ``dev`` lembre-se de fechá-la após
  seu PR ser aceito!

.. _README.rst: README.rst
