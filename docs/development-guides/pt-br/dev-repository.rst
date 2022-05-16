#####################
Repositório de código
#####################

.. contents::
   :depth: 2


*******************
Política de Commits
*******************

Adota-se para este projeto padrões para o comentário e execução dos commits. O idioma padrão para efetuar commits neste repositório é o inglês.

As mensagens devem ser sucintas e expressarem de forma clara e objetiva a ação do commit.

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

********************
Política de Branches
********************

O repositório possui uma branch `prod`, que possui objetivo de manter a versão estável do projeto.
Possui também uma branch para desenvolvimento chamada `develop`, cujo objetivo é manter-se atualizada.
Desta forma nenhum commit deve ser efetuado diretamente nestas branchs. 
As alterações devem ser criadas inicialmente em branchs de funcionalidades ou de configuração e correção, toda branch de funcionalidade deve ser criada a partir da branch develop. 


Após a etapa de desenvolvimento em uma branch de funcionalidade ser concluída, deve ser submetido um merge request. 
Ele deve ser conferido por um membro da equipe e se estiver em conformidade, é aceito. 

**************************************
Padrão para criação e uso das branches
**************************************

Devem seguir a nomenclatura padrão abaixo, redigidas no idioma inglês. 

O código das branchs deve estar sincronizado com alguma Issue do repositório, sendo então o nome padrão para as branchs no formato:  
*validate-username-issue-222*
*create-cluster-group-issue123*

************************************
Automatização de Fechamento de Issue
************************************

Caso termine sua funcionalidade e deseje fechar a Issue automaticamente é possivel através das palavras chaves na descrição do commit:  
`resolves: #numeroDaIssue`  
Em caso de múltiplas issues é necessário replicar o comando:  
`resolves: #numeroDaIssue`  
`resolves: #numeroDaIssue2`  
`resolves: #numeroDaIssue3`  

*****************************
Conflitos nos Merge-requests
*****************************

A branch do MR deve estar sempre atualizado com a branch de desenvolvimento (develop) em caso de conflitos, deve-se realizar um rebase na branch com a develop
