from django.db import models
from model_utils import Choices
from model_utils.fields import StatusField

from boogie import rules
from boogie.rest import rest_api

@rest_api(
    ['id', 'name', 'candidacy', 'urn', 'party', 'image',
     'has_clean_pass', 'committed_to_democracy', 'uf',
     'adhered_to_the_measures', 'site_url', 'youtube_url', 'facebook_url',
     'crowdfunding_url', 'twitter_url', 'instagram_url']
)
class Candidate(models.Model):

    """A political candidate. """

    def __str__(self):
        return "%s - %s" % (self.name, self.party)

    CANDIDACY_OPTIONS = Choices('SENADOR(A)', 'DEPUTADO(A)')
    PARTY_OPTIONS = Choices('PT', 'PSDB')
    POLITICAL_OPTIONS = Choices('SIM', 'NÃO', 'SEM RESPOSTA')

    name = models.CharField(max_length=100,
                            help_text="The name of the candidate")
    candidacy = StatusField(choices_name='CANDIDACY_OPTIONS',
                            help_text="the candadite candidacy")
    urn = models.IntegerField(help_text="The candidate urn number")
    party = StatusField(choices_name='PARTY_OPTIONS',
                        help_text="The candidate party initials")
    image = models.FileField(upload_to="candidates", default="card_avatar-default.png")
    has_clean_pass = StatusField(choices_name='POLITICAL_OPTIONS')
    committed_to_democracy = StatusField(choices_name='POLITICAL_OPTIONS')
    adhered_to_the_measures  = StatusField(choices_name='POLITICAL_OPTIONS')
    site_url = models.CharField(max_length=100,
                                help_text="The site of the candidate",
                                default="")
    uf = models.CharField(max_length=2,
                          help_text="The candidate uf",
                          default="")
    crowdfunding_url = models.CharField(max_length=60,
                                        help_text="The candidate crowdfunding",
                                        default="")
    facebook_url = models.CharField(max_length=60,
                                    help_text="The candidate facebook page",
                                    default="")
    twitter_url = models.CharField(max_length=60,
                                   help_text="The candidate facebook page",
                                   default="")
    instagram_url = models.CharField(max_length=60,
                                     help_text="The candidate instagram page",
                                     default="")
    youtube_url = models.CharField(max_length=60,
                                   help_text="The candidate instagram page",
                                   default="")
    public_email = models.CharField(max_length=60,
                                   help_text="The candidate public email",
                                   default="ricardo@cidadedemocratica.org.br")

# boogie decorator to add a property on model serializer
@rest_api.property(Candidate)
def score(object):
    if (object.has_clean_pass == "SIM" \
            and object.committed_to_democracy == "SIM" \
            and object.adhered_to_the_measures == "SIM"):
        return 'good'
    if (object.has_clean_pass == "NÃO" \
            or object.committed_to_democracy == "NÃO" \
            or object.adhered_to_the_measures == "NÃO"):
        return 'bad'
    return 'partial'
