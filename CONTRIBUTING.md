## Adicionar funcionalidades no ej-server

Para cada issue a ser resolvida, seguir o seguinte procedimento:

- Clone o repositório
- Mude a branch local para ``dev`` ou qualquer outra que queira criar para
  resolver sua issue específica. E.g.:
```
$ git checkout dev
```
- Prepare o ambiente como é explicado no [README.rst](README.rst)
- Instale os hooks para checar estilo ``flake8`` com:
```
$ inv install-hooks
```
- Sempre rode os testes antes de fazer qualquer commit (rode mesmo porque seu
  PR não será aceito se seus testes não estiverem passando!)
  ```
  $ inv test
  ```
- Ao terminar sua issue, para enviar para a branch MASTER, abra um ticket de
pull request no github com o sentido (base <- head):

 ```
 unb-cic-esw/youtube-data-monitor/master <- unb-cic-esw/youtube-data-monitor/dev
 ```

- Espere o Travis CI, GitLab CI e o Code Climate executar os testes de integração
- Se os testes passarem, você ou outro contribuidor estarão livres para
aceitar seu PR :rocket:
- Se a branch que criou não for a ``dev`` lembre-se de fechá-la após seu PR ser
aceito!
