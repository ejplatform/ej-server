########################
Guia de desenvolvimento
########################

Você pode visitar o website da EJ em https://ejplatform.org.

Antes de tudo, é interessante entender o fluxo de uso da EJ, em mais alto nível
para que depois entremos em detalhes de implementação.

A aplicação foi desenvolvida tendo como pilar principal a coleta de opinião. Para que ela seja realizada,
é criada uma conversa, que possua uma frase chamativa para iniciar uma discussão.
A partir dela, pessoas podem introduzir comentários e também votar em comentários de outras pessoas, 
caso elas concordem ou discordem.

Para que possam participar, os usuários precisam estar autenticados, por meio de um perfil, 
e também podem ganhar pontos por meio de um sistema de gamificações, para engajar ainda mais 
durante suas participações.

A partir de todos os dados coletados, é possível traçar perfis de opinião. Além dos perfis,
há outras possibilidades de análise e relatório de dados.

.. toctree::

   getting-started
   architecture
   dev-repository
   dev-integration
   environment-variables
   translations
   urls
   social-login
   themes
   dev-style