import dramatiq

from boogie.configurations import Conf, env


class DramatiqConf(Conf):
    """
    Class to set setting for the Dramatiq that is a
    distributed task processing library
    https://dramatiq.io/
    """
    DRAMATIQ_BROKER_URL = env("", name="{name}")
    DRAMATIQ_BROKER_TYPE = env("stub", name="{name}")
    DRAMATIQ_BROKER_HOST = env("", name="{name}")
    DRAMATIQ_BROKER_PORT = env(0, name="{name}")

    url = None
    kind = None
    host = None
    port = None 
    kwargs = None
    broker = None

    def set_broker_atribs(self):
        """
        This method sets the url, kind, host and port attributes for the broker object
        """ 
        self.set_broker_url()
        

    def set_broker_url(self):
        """
        This method checks extract the broker url and sets to the url variable
        """ 
        if self.DRAMATIQ_BROKER_URL:
            self.url = self.DRAMATIQ_BROKER_URL.strip()
            self.set_atribs()
        else:
            self.kind = self.DRAMATIQ_BROKER_TYPE
            self.host = self.DRAMATIQ_BROKER_HOST or None
            self.port = self.DRAMATIQ_BROKER_PORT or None

    def set_atribs(self):
        """
        This method checks if the url is none, then sets the kind, host and port attributes 
        for the broker object
        """ 
        if self.url is None:
                self.kind, self.host, self.port = "stub", None, None
        else:
            self.kind, _, self.url = self.url.partition("://")
            self.host, _, self.port = self.url.partition(":")
            self.host = self.host or None
            self.port = int(self.port) if self.port else None

    def separate_non_null_args(self):
        """
        This method separates the non null arguments in the kwargs dict
        """ 
        self.kwargs = [("self.host", self.host), ("port", self.port)]
        self.kwargs = {k: v for k, v in self.kwargs if v is not None}

    def initialize_broker(self):
        """
        This method initializes the broker object
        """ 
        if self.kind == "stub":
            from dramatiq.brokers.stub import StubBroker
            self.broker = StubBroker()
        elif self.kind == "redis":
            from dramatiq.brokers.redis import RedisBroker
            self.broker = RedisBroker(**self.kwargs)
        elif self.kind == "rabbitmq":
            from dramatiq.brokers.rabbitmq import RabbitmqBroker
            self.broker = RabbitmqBroker(**self.kwargs)
        else:
            raise ValueError(f"invalid dramatiq broker: {self.kind}")

    def get_dramatiq_broker_object(self):
        """
        This method initializes the broker object for Dramatiq and saves it in
        Django's settings.
        """
        self.set_broker_atribs()

        self.separate_non_null_args()

        self.initialize_broker()

        # Configure as default and exit
        dramatiq.set_broker(self.broker)

        return self.broker

        

        
