import collections


class Store(collections.Mapping):
    """
    A cache that keeps the most recently used objects.
    """

    def __init__(self, function, max_size=256):
        self._data = {}
        self._order = []
        self.function = function
        self.max_size = max_size

    def __missing__(self, key):
        self._data[key] = value = self.function(key)
        return value

    def __getitem__(self, item):
        order = self._order
        try:
            value = self._data[item]
            if item != order[-1]:
                del order[order.index(item)]
                order.append(item)
        except KeyError:
            self._data[item] = value = self.function(item)
            order.append(item)

            while len(order) > self.max_size:
                del self._data[order.pop(0)]
        return value

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)

    def update_item(self, key, function):
        """
        Apply function to item in the given key and update result.
        """
        data = self[key]
        self[key] = function(data)
