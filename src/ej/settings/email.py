from boogie.configurations import Conf, env


class EmailConf(Conf):

    #
    # E-mail settings
    #
    EMAIL_HOST = env('', name='EMAIL_HOST')
    EMAIL_PORT = env(587, name='EMAIL_PORT')
    EMAIL_HOST_USER = env('', name='EMAIL_HOST_USER')
    EMAIL_HOST_PASSWORD = env('', name='EMAIL_HOST_PASSWORD')
    EMAIL_USE_SSL = env(False, name='EMAIL_USE_SSL')
    EMAIL_USE_TLS = env(False, name='EMAIL_USE_TLS')
