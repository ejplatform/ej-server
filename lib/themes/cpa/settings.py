from environ import Env

env = Env(DEBUG=(bool, False))

print('Executing custom settings for theme CPA')

# Override EJ configurtions
CPA_SHOW_START_PAGE_EXPLANATION_BANNER = env('CPA_SHOW_START_PAGE_EXPLANATION_BANNER', default=True)
EJ_ANONYMOUS_HOME_PATH = env('EJ_ANONYMOUS_HOME_PATH', default='/start/')
EJ_PAGE_TITLE = env('EJ_PAGE_TITLE', default='Plataforma CPA')
EJ_REGISTER_TEXT = env('EJ_REGISTER_TEXT', default='Não faz parte da Plataforma CPA?')
EJ_LOGIN_TITLE_TEXT = env('EJ_LOGIN_TITLE_TEXT', default='Participe dos debates, contribua para promover e defender seus direitos')
EJ_EXCLUDE_PROFILE_FIELDS = env('EJ_EXCLUDE_PROFILE_FIELDS', default=['political_activity'])
EJ_MAX_BOARD_NUMBER = env('EJ_MAX_BOARD_NUMBER', default=0)
EJ_STATE_MAX_LENGTH = env('EJ_STATE_MAX_LENGTH', default=2)
EJ_STATE_CHOICES = (
    ('AC', 'Acre'),
    ('AL', 'Alagoas'),
    ('AP', 'Amapá'),
    ('AM', 'Amazonas'),
    ('BA', 'Bahia'),
    ('CE', 'Ceará'),
    ('DF', 'Distrito Federal'),
    ('ES', 'Espírito Santo'),
    ('GO', 'Goiás'),
    ('MA', 'Maranhão'),
    ('MT', 'Mato Grosso'),
    ('MS', 'Mato Grosso do Sul'),
    ('MG', 'Minas Gerais'),
    ('PA', 'Pará'),
    ('PB', 'Paraíba'),
    ('PR', 'Paraná'),
    ('PE', 'Pernambuco'),
    ('PI', 'Piauí'),
    ('RJ', 'Rio de Janeiro'),
    ('RN', 'Rio Grande do Norte'),
    ('RS', 'Rio Grande do Sul'),
    ('RO', 'Rondônia'),
    ('RR', 'Roraima'),
    ('SC', 'Santa Catarina'),
    ('SP', 'São Paulo'),
    ('SE', 'Sergipe'),
    ('TO', 'Tocantins'),
)
