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
class SelectedCandidate(models.Model):

    """Candidates selected by a user"""
    def __str__(self):
        return "%s - %s" % (self.candidate.name, self.candidate.party)

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, null=True)

@receiver(post_save, sender=SelectedCandidate)
def send_message(sender, instance, created, **kwargs):
    if created:
        user = instance.user
        title = instance.candidate.name
        url = instance.candidate.site_url
        try:
            channel = Channel.objects.filter(owner=user, sort="selected")[0]
        except IndexError:
            channel = Channel.objects.create(name="selected channel", sort="selected", owner=user)
            channel.users.add(user)
            channel.save()
        Message.objects.create(channel=channel, title=title, body=url)

@receiver(post_save, sender=SelectedCandidate)
def send_selected_email(sender, instance, created, **kwargs):
    candidate_email = [instance.candidate.public_email]

    html_message = '<html><body><div><p>Boas notícias! Você acaba \
    de ser selecionada por um usuário no aplicativo da campanha Unidos \
    Contra a Corrupção, o que significa que essa pessoa se interessou \
    pelo seu perfil e pelos seus compromissos e agora vai poder ver \
    mais detalhes e informações sobre você.</p><p>Atenciosamente.\
    <br>Unidos Contra a Corrupção</p></div></body></html>'
    send_mail(
        'Você foi selecionado por uma pessoa da campanha Unidos Contra a Corrupção',
        '',
        'Unidos contra a corrupção <noreply@unidoscontraacorrupcao.org.br>',
        candidate_email,
        fail_silently=False,
        html_message=html_message
    )
