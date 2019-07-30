class LevelMixin:
    """
    Basic abstract interface to all Level track enums.

    They all have a few properties in common:

        * The minimum interface defined by this class
        * Start at the first level NONE, represented as zero.
        * Have four more levels afterwards.
    """

    @classmethod
    def check_level(cls, data):
        """
        Checks the level from arguments.
        """
        raise NotImplementedError

    @classmethod
    def skipping_none(cls):
        it = iter(cls)
        next(it)
        yield from it

    def achieve_next_level_msg(self, data):
        """
        Message that explains what user needs to do to achieve the next level.
        """
        raise NotImplementedError
