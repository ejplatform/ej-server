from django.db import models
from ej_users.models import User
from .candidate import Candidate
from django.db.models.signals import post_save
from django.dispatch import receiver
from ej_messages.models import Message
from ej_channels.models import Channel
from django.core.mail import send_mail

from boogie import rules
from boogie.rest import rest_api

@rest_api()
class PressedCandidate(models.Model):

    """Candidates pressed by a user"""
    def __str__(self):
        return "%s - %s" % (self.candidate.name, self.candidate.party)

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, null=True)

@receiver(post_save, sender=PressedCandidate)
def send_message(sender, instance, created, **kwargs):
    if created:
        user = instance.user
        title = instance.candidate.name
        url = instance.candidate.site_url
        try:
            channel = Channel.objects.filter(owner=user, sort="press")[0]
        except IndexError:
            channel = Channel.objects.create(name="press channel", sort="press", owner=user)
            channel.users.add(user)
            channel.save()
        Message.objects.create(channel=channel, title=title, body="")

@receiver(post_save, sender=PressedCandidate)
def send_press_email(sender, instance, created, **kwargs):
    candidate_email = [instance.candidate.public_email]
   
    html_message = '<html><body><div><p>Um usuário acaba \
    de solicitar que você se comprometa com os compromissos da \
    campanha Unidos Contra a Corrupção. Essa pessoa conheceu \
    seu perfil e gostaria de pedir que registre seu compromisso.</p>\
    <p>Quando registrar o compromisso, todos os usuários que fizeram \
    essa solicitação receberão avisos diretamente, podendo avaliar \
    positivamente seu perfil! Não perca tempo e registre seu \
    compromisso agora mesmo:</p><p><a href="https://unidoscontraacorrupcao.org.br">\
    Unidos Contra a Corrupção</a></p><p>Atenciosamente.\
    <br>Unidos Contra a Corrupção</p></div></body></html>'
    send_mail(
        'Você recebeu um pedido de uma pessoa da campanha Unidos Contra a Corrupção',
        '',
        'Unidos contra a corrupção <noreply@unidoscontraacorrupcao.org.br>',
        candidate_email,
        fail_silently=False,
        html_message=html_message
    )