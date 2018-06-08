from django.db.models import QuerySet, Manager

from sidekick import import_later

pd = import_later('pandas')


class ClusterQuerySet(QuerySet):
    pass


class ClusterManager(Manager.from_queryset(ClusterQuerySet)):
    def votes_data(self, conversation):
        """
        Return a query set of (cluster, comment, choice) items from the given
        conversation.
        """
        return conversation.votes.values_list(
            'comment__conversation__',
            'comment_id',
            'choice',
        )

    def votes_dataframe(self, conversation):
        """
        Like .votes_data(), but Return a dataframe.
        """
        data = list(self.votes_data(conversation))
        return pd.DataFrame(data, columns=['cluster, comment', 'choice'])
