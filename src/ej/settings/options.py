from boogie.configurations import Conf, env


class EjOptions(Conf):
    """
    Options for EJ installation.
    """

    EJ_ENABLE_ROCKETCHAT = env(True)
