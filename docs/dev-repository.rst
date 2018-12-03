Repositório de código
=====================

.. contents::
   :depth: 2



Política de Commits
-------------------

Adota-se para este projeto padrões para o comentário e execução dos commits. O idioma padrão para efetuar commits neste repositório é o inglês. As mensagens devem ser sucintas e expressarem de forma clara e objetiva a ação do commit.

Como exemplo, considere o trabalho da construção de uma tela inicial da aplicação. O commit deverá ser efetuado como segue:
```
git commit -m "Create new home Screen"
```

Atente ainda para os seguintes aspectos:
* O commit deve iniciar com letras maiúsculas.
* O commit deve iniciar com verbo no infinitivo.

Exemplos:  
-"Fix login auth error"  
-"Create User model"  
-"Refactor profile View"  
-"Translate flat pages"    

Política de Branches
--------------------

O repositório possui uma branch `master`, que possui objetivo de manter a versão estável do projeto.
Possui também uma branch para desenvolvimento chamada `devel`, cujo objetivo é manter-se atualizada.
Desta forma nenhum commit deve ser efetuado diretamente nestas branchs. As alterações devem ser criadas inicialmente em branchs de funcionalidades ou de configuração e correção, toda branch de funcionalidade deve ser criada a partir da branch devel. 

A imagem a seguir, ilustra como deve ser a organização das branchs e os eventos de criação e merge de acordo com o [Git Flow](https://leanpub.com/git-flow/read).
[[https://leanpub.com/site_images/git-flow/git-workflow-release-cycle-2feature.png]]

Como pode ser visto, após a etapa de desenvolvimento em uma branch de funcionalidade ser concluída, deve ser submetido um pull request em caso de alguma revisão ou merge da mesma. O pull request deve ser conferido por um membro da equipe e se estiver em conformidade, então o pull request é aceito. 

Padrão para criação e uso das branches
--------------------------------------

Deve-se criar novas branches para trabalho em seguindo padrão [GitFlow](https://datasift.github.io/gitflow/IntroducingGitFlow.html). Estas devem ser criadas a partir da branch __develop__, e devem seguir a nomenclatura padrão abaixo, redigidas no idioma inglês. 

O código das branchs deve estar sincronizado com alguma Issue do repositório, sendo então o nome padrão para as branchs no formato:  
__i401_validate_username__  
__i397_create_cluster_group__

Automatização de Fechamento de Issue
------------------------------------

Caso termine sua funcionalidade e deseje fechar a Issue automaticamente é possivel através das palavras chaves na descrição do commit ou pull request:  
`resolves: #numeroDaIssue`  
Em caso de múltiplas issues é necessário replicar o comando:  
`resolves: #numeroDaIssue`  
`resolves: #numeroDaIssue2`  
`resolves: #numeroDaIssue3`  


Pull-requests tempestivos e permanentes
---------------------------------------

Nesse projeto adotamos a política dos pull requests tempestivos e permanentes, ou seja, a partir do primeiro commit deve ser criado o pull request de merge da branch da issue com a develop. Esse pull request é, portanto, tempestivo - criado no primeiro commit - e permanente - permanece aberto enquanto o trabalho da issue estiver sendo executado. Além disso, sugere-se, para alterações no frontend, o envio também de prints ou gifs que ajudem a entender o trabalho realizado.

O autor do pull request deve assignar o grupo de revisão: https://github.com/orgs/ejplatform/teams/revision


Conflitos nos Pull-requests
---------------------------

A branch do PR deve estar sempre atualizado com a branch de desenvolvimento (develop) em caso de conflitos, deve-se realizar um rebase na branch com a develop

'''Exceções: commits que podem ser feitos diretamente na devel'''

- Fix de conteúdo e css (não arquiteturais)
- Tradução
- Cobertura de teste
- Atualizar assets
- Commits de melhoramentos/bugfix de pipeline (que precisam ser commitados na branch do pipeline)


Release cycle
-------------

O EJ vai ter como meta um release mensal. Então o nosso release cycle é de 4 semanas, sendo 3 semanas para desenvolvimento das features e validação dos PRs de produto (os que são submetidos da develop pra master) e a última semana do mês para a definição do release candidate a partir dos PRs incluidos na master.

'''Trabalho no board e validações de UX'''

O board segue no mesmo lugar: https://github.com/ejplatform/ej-server/projects/1?fullscreen=true
Ele já está automatizado para carregar as issues fechadas pra coluna de staging. A coluna de staging é onde acontecem as validações de ux das features. Uma vez validadas, o grupo de ux transporta pra done.

'''Validações de produto'''

As validações de produto acontecem motivadas pelos PRs do develop para a master. Sempre que um revisor fizer o merge dos PRs vindos das branches de issue pra develop, gera um PR correspondente pra master, acionando a validação de produto, focada na release.

