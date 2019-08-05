from boogie.models import QuerySet


class ProgressQuerySet(QuerySet):
    def sync_and_save(self):
        """
        Synchronize and save all elements from queryset.

        Return a list of saved elements.
        """

        elems = [e.sync() for e in self]
        self.bulk_update(elems, ["score", *self.model.level_field_names()])
        return elems
