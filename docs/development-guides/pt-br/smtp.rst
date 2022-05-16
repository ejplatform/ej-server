Configurando o servidor SMTP
-----------------------------

A EJ depende de um servidor SMTP para realizar algumas operações como recuperação de senha.
Para isso é preciso indicar qual o servidor será utilizado. Essa configuração é feita por
meio das seguintes variáveis de ambiente, definidas no arquivo :code:`variables.env`: 

- SMTP_DEFAULT_EMAIL
- SMTP_HOST_EMAIL
- SMTP_HOST
- SMTP_PORT
- SMTP_HOST_EMAIL
- SMTP_HOST_PASSWORD
- SMTP_DEFAULT_NAME

Essas variáveis serão carregadas pela classe de configuração :code:`EmailConf`, presente 
em :code:`src/ej/settings/email.py`. Você pode utilizar qualquer servidor SMTP como, por exemplo, 
o servidor do Google. Caso você opte por utilizar o servidor do Google, 
é necessário fazer a configuração de **aplicativos inseguros**.
