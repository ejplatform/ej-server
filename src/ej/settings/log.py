from boogie.configurations import LoggingConf as Base


class LoggingConf(Base):
    """
    Logging configuration
    """

    def get_logging(self):
        """
        Return the information for the logger
        :return: loggers
        """
        return {
            "version": 1,
            "disable_existing_loggers": False,
            "handlers": {
                "file": {
                    "level": "DEBUG",
                    "class": "logging.FileHandler",
                    "filename": self.LOG_DIR / "debug.log",
                },
                "console": {"level": "DEBUG", "class": "logging.StreamHandler"},
            },
            "loggers": {
                "ej": self.DEBUG_LOGGER,
                "django": self.DEFAULT_LOGGER,
                "celery": self.DEFAULT_LOGGER,
            },
        }
