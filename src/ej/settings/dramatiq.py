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

    def get_dramatiq_broker_object(self):
        """
        This method initializes the broker object for Dramatiq and saves it in
        Django's settings.
        :return: broker
        """

        if self.DRAMATIQ_BROKER_URL:
            url = self.DRAMATIQ_BROKER_URL.strip()
            if url is None:
                kind, host, port = "stub", None, None
            else:
                kind, _, url = url.partition("://")
                host, _, port = url.partition(":")
                host = host or None
                port = int(port) if port else None
        else:
            kind = self.DRAMATIQ_BROKER_TYPE
            host = self.DRAMATIQ_BROKER_HOST or None
            port = self.DRAMATIQ_BROKER_PORT or None

        # Separate non-null args
        kwargs = [("host", host), ("port", port)]
        kwargs = {k: v for k, v in kwargs if v is not None}

        # Initializes broker
        if kind == "stub":
            from dramatiq.brokers.stub import StubBroker

            broker = StubBroker()
        elif kind == "redis":
            from dramatiq.brokers.redis import RedisBroker

            broker = RedisBroker(**kwargs)
        elif kind == "rabbitmq":
            from dramatiq.brokers.rabbitmq import RabbitmqBroker

            broker = RabbitmqBroker(**kwargs)
        else:
            raise ValueError(f"invalid dramatiq broker: {kind}")

        # Configure as default and exit
        dramatiq.set_broker(broker)
        return broker
