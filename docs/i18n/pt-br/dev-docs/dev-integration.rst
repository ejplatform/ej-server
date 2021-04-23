************
Integrações
************

.. contents::
   :depth: 2



Middlewares do EJ
=================

Middlewares são uma camada em que toda request passa antes de chegar no processamento denido para determinada rota no servidor.
Ex.: acessar https://www.ejplatform.org/conversations/servicos-publicos-futuro/ antes de chegar na rota definida para esta url,
um middleware executa um determinado processamento.

O django oferece um sistema de middleware bastante interessante e de razoavelmente fácil utilização, onde no arquivo de configuração
existe uma lista de middlewares que o django utilizará.

Por que usar middlewares?
-------------------------

Os middlewares são bastante interessantes quando se deseja fazer uma lógica diferenciada para o processamento das urls ou adicionar
alguma lógica pré-processamento de rotas.

Por que usamos middlewares no EJ?
---------------------------------

Nós temos algumas lógicas de url um pouco diferentes, por exemplo, os urls de conversa são case insensitive, o que significa que
se acessarmos https://www.ejplatform.org/conversations/servicos-publicos-futuro/ ou https://www.ejplatform.org/conversations/Servicos-Publicos-Futuro/
acessamos a mesma conversa.

Além de urls de conversa, os quadros de conversa também possuem link case insensitive https://www.ejplatform.org/semanadeinovacao/ e https://www.ejplatform.org/Semanadeinovacao/ dão no mesmo.

Como conseguimos isso?
----------------------

Nos middlewares de board e conversations, sempre que uma resposta for dar 404, a gente pega a url da um split por '/' aplicamos um slugify em todos os termos gerados e montamos uma nova url. Com a função ```resolve()``` do django conseguimos como retorno qual é a view_function responsável por esta url e assim conseguimos processar corretamente a url.


Hyperpython
===========

[Hyperpython](https://github.com/fabiommendes/hyperpython) é uma biblioteca que fornece maneiras de se escrever HTML utilizando python (assim como o hyperscript faz na linguagem javascript).

Esta biblioteca foi criada pelo professor [Fabio](https://github.com/fabiommendes) com o intuito de reduzir a utilização de templates, tendo em vista que templates separam tecnologias e não preocupações. Assim apenas separar html ou linguagem de template do código em si não resolve alguns problemas de reuso de código e arquitetura do projeto.

Com o hyperpython nós conseguimos criar funções puramente python que servem como componentes view da aplicação, possibilitando a execução de toda uma lógica dentro desta função.

Para visualizar melhor, vamos pensar em um exemplo:

Imagina que seria legal ter um componente que renderiza uma lista de itens como uma lista que colapsa, essa lista é utilizada em vários lugares da nossa aplicação, modificando os itens e talvez o estilo.

Se fossemos utilizar uma linguagem de template como o jinja2, teríamos que criar uma macro que recebe uma lista de itens, fazer um for, talvez um if, tudo isso utilizando a syntaxe de template que não é muito amigável para contemplar toda essa lógica.

Utilizando o hyperpython, podemos usar uma função comum do python:

.. code-block:: python

  def collapsible_list(item_list, title=None, **kwargs):
    data = [h2(x) for x in item_list]
    return div(
      class_='CollapsibleList',
      is_component=True
    )[
      div(class_='CollapsibleList-data')[
        html_list(data),
      ]
    ]


E algo muito legal também é que podemos criar `roles` das funções. Roles são papéis que determinados objetos podem assumir na view do sistema, por exemplo um objeto de conversa pode assumir um papel de exibição em balão e pode assumir um papél de exibição em card.

.. code-block:: python

  from hyperpython import html, div, h2, Text, span
  from . import model

  @html.register(model.Conversation, role='balloon')
  def conversation_balloon(conversation):
    return (
      div(
        class_='Conversation-balloon
        is_component=True
      )[
        h2(conversation.title),
        Text(conversation.content)
      ]
    )
    
  @html.register(model.Conversation, role='card')
  def conversation_card(conversation):
    return (
      div(
        class_='Conversation-card
        is_component=True
      )[
        h1(conversation.title),
        span(conversation.description)
      ]
    )
 

Com algumas configurações na linguagem de template, conseguimos utilizar as `roles` da seguinte maneira:

.. code-block:: jinja2 

  {{conversation|balloon}}


.. code-block:: jinja
  {{conversation|card}}


No EJ a maior parte do uso do hyperpython com roles é no app ej_conversations, onde fazemos coisas parecidas como no exemplo, a diferença é que nós estamos usando uma versão modificada onde conseguimos usar templates como componentes.
