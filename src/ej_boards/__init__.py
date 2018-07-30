from sidekick import import_later

_db = import_later('.models', package=__package__)
default_app_config = 'ej_boards.apps.EjBoardsConfig'
