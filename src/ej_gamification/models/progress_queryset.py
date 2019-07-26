from boogie.models import QuerySet


class ProgressQuerySet(QuerySet):
    def sync_and_save(self):
        """
        Synchronize and save all elements from queryset.
        """

        def sync_and_save(x):
            x.sync_and_save()
            return x

        return self.map(sync_and_save)
