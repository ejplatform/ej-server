# Fale Conosco

Para entrar em contato com o CONANDA, envie um e-mail para <b>xxx@xxx.gov.br</b> ou ligue no telefone <b>(61)xxxxxxxx</b>.

Para falar com o Conselho de Participação de Adolescentes, o e-mail é <b>contato@participacpa.gov.br</b>.

Para dúvidas, críticas e sugestões sobre a plataforma, utilize o formulário abaixo. Responderemos o mais rápido possível para o e-mail cadastrado no seu perfil.


<form id="emailsending-form" onsubmit="return sendEmail()" style="display: flex; justify-content: center; flex-direction: column;">
    <input id="subject" type="text" placeholder="assunto" style="border: 1px solid #30BFD3" />
    <textarea id="message" rows="6" cols="50" placeholder="mensagem" style="border: 1px solid #30BFD3"></textarea>
    <input type="submit" class="Button" value="ENVIAR" style="margin: 0 auto; width: 50%; background-color: #8EC73F;"/>
</form>

# Denúncias

Para denúncias <b>Disque</b> 100 e <b>#HUMANIZAREDES.</b>

<script>
    function sendEmail() {
        console.log($("#subject").val());
        console.log($("#message").val());

        const sucessMessage = 
        `
            <div style="padding: 10px;
            border: 1px solid #30BFD3;
            border-radius: 12px; 
            text-align: center;">
            <i class="fas fa-envelope fa-3x" style="background-color: #8EC73F; color: #fff; padding: 8px; border-radius: 12px;"></i>
            <p>
                Obrigada. Sua mensagem foi enviada com sucesso! 
                Responderemos o mais rápido o possível
            </p>
            </div>
        `

        $('#emailsending-form').replaceWith(sucessMessage);


        return false;
    }
</script>