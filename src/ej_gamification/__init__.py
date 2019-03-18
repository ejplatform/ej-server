from sidekick import import_later as _import_later

# Import public functions from inner apps
_import = lambda x: _import_later(x, package=__package__)

# Participation
get_participation = _import('.models:get_participation')
get_progress = _import('.models:get_progress')

# Endorsements
endorse_comment = _import('.models:endorse_comment')
is_endorsed = _import('.models:is_endorsed')

# App config
default_app_config = 'ej_gamification.apps.EjGamificationConfig'
