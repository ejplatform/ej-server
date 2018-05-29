from boogie.configurations import LoggingConf as Base


class LoggingConf(Base):
    """
    Logging configuration
    """

    @property
    def LOGGING(self):
        return {
            'version': 1,
            'disable_existing_loggers': False,
            'handlers': {
                # 'file': {
                #     'level': 'DEBUG',
                #     'class': 'logging.FileHandler',
                #     'filename': ROOT_DIR / 'local/debug.log',
                # },
                'console': {
                    'level': 'DEBUG',
                    'class': 'logging.StreamHandler',
                },
            },
            'loggers': {
                'ej': self.DEBUG_LOGGER,
                'django': self.DEFAULT_LOGGER,
                'celery': self.DEFAULT_LOGGER,
            },
        }
