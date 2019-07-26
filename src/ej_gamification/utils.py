class compute_points:
    __slots__ = ("multiplier", "delegate_name", "own_name")

    def __init__(self, multiplier, name=None, own_name=None):
        self.multiplier = multiplier
        self.delegate_name = name
        self.own_name = own_name

    def __get__(self, obj, cls=None):
        if obj is None:
            return self

        raw = getattr(obj, self.delegate_name)
        return raw * self.multiplier

    def __set_name__(self, owner, name):
        if self.own_name is None:
            self.own_name = name
        if self.delegate_name is None:
            self.delegate_name = "n" + self.own_name[3:]
