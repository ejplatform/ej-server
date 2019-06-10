from itertools import chain
from logging import getLogger

from django.contrib.auth import get_user_model
from django.db import transaction
from sidekick import import_later

from boogie.models import QuerySet, F, Manager
from ej_conversations.math import imputation
from ej_conversations.models import Conversation
from ..mixins import ClusterizationBaseMixin

pd = import_later("pandas")
np = import_later("numpy")
clusterization_pipeline = import_later(
    "..math:clusterization_pipeline", package=__package__
)
models = import_later(".models", package=__package__)
log = getLogger("ej")


class ClusterQuerySet(ClusterizationBaseMixin, QuerySet):
    """
    Represents a table of Cluster objects.
    """

    clusters = lambda self: self

    def users(self, by_comment=False):
        """
        Queryset of users explicitly clusterized in the current cluster set.
        """
        if by_comment:
            return super().users(by_comment)
        return get_user_model().objects.filter(clusters__in=self)

    def participants(self):
        """
        Queryset with all participants of the conversations associated
        with the current cluster set.
        """
        return super().users()

    def check_unique_clusterization(self):
        """
        Raise ValueError if cluster set does *NOT* belong to a single
        clusterization.
        """
        # Fast-track without touching the database if this is a related
        # query from a Clusterization object.
        related = self._known_related_objects
        if len(related) == 1:
            # noinspection PyProtectedMember
            data = related.get(self.model._meta.get_field("clusterization"))
            if data is not None and len(data) == 1:
                return

        # Otherwise we check in the database if we can find more than one
        # clusterization root
        if self.values_list("clusterization").distinct().count() > 1:
            msg = "more than one clusterization found on dataset"
            raise ValueError(msg)

    def conversations(self):
        return Conversation.objects.filter(clusterization__clusters__in=self)

    def votes_data(self, conversation=None):
        """
        Return a query set of (cluster, comment, choice) items from the given
        conversation.
        """
        return conversation.votes.values_list(
            "comment__conversation_id", "comment_id", "choice"
        )

    def votes_dataframe(self, conversation):
        """
        Like .votes_data(), but Return a dataframe.
        """
        data = list(self.votes_data(conversation))
        return pd.DataFrame(data, columns=["cluster, comment", "choice"])

    def votes_table(
        self,
        data_imputation=None,
        cluster_col="cluster",
        kind_col=None,
        mean_stereotype=False,
        non_classified=False,
        check_unique=True,
        **kwargs
    ):
        """
        Return a votes table that joins the results from regular users
        and stereotypes. Stereotypes are identified with negative index labels.

        It accepts the same methods as votes_table() function.

        Args:
            data_imputation ({'mean', None}):
                Data imputation method for filling missing values.
            mean_stereotype (bool):
                If True, uses the average stereotype vote at each cluster as
                the stereotype rows. If this is set, stereotypes are
                identified by the cluster index instead of the stereotype index.
            non_classified (bool):
                If True, include users that were not clusterized in the current
                cluster set. Otherwise only return users explicitly present on
                the current clusters.
            check_unique (bool):
                Raises a ValueError if clusters do not have a common
                root (default). If set to False, skip this test. NOTE: if cluster
                set has more than one root, users can be on multiple clusters,
                which can lead to non-determinism on the cluster label assigned
                to user.
            cluster_col (str, None):
                Name of the column that identifies the cluster of each
                user/stereotype. Set to None to disable it.
            kind_col (str, None):
                If True, instead of using negative indexes to differentiate
                users from stereotypes, it adds an extra column with the given
                name with a boolean which is True when then entry is an user
                and False otherwise.
        """

        # Select comments
        if "comments" in kwargs:
            raise TypeError("invalid argument: comments")
        kwargs["comments"] = self.comments()

        # Checks
        if check_unique:
            self.check_unique_clusterization()

        # Fetch votes from database
        kwargs.update(kind_col=kind_col, cluster_col=cluster_col)
        stereotype_votes = self._stereotypes_votes_table(mean_stereotype, **kwargs)
        user_votes = self._users_votes_table(non_classified, **kwargs)

        # Imputation must occur after both set of votes are joined together.
        votes = user_votes.append(stereotype_votes)
        return imputation(votes, data_imputation)

    def _stereotypes_votes_table(self, mean, kind_col, cluster_col, **kwargs):
        # Prepare stereotype votes
        if mean:
            stereotype_votes = self.mean_stereotypes_votes_table()
        else:
            stereotypes = self.stereotypes()
            stereotype_votes = stereotypes.votes_table(**kwargs)
        if kind_col:
            stereotype_votes[kind_col] = False
        else:
            stereotype_votes.index *= -1
        if cluster_col is not None:
            clusters = self.dataframe("id", index="stereotypes")
            if not kind_col:
                clusters.index *= -1
            stereotype_votes[cluster_col] = clusters
        return stereotype_votes

    def _users_votes_table(self, non_classified, kind_col, cluster_col, **kwargs):
        users = self.participants() if non_classified else self.users()
        user_votes = users.votes_table(**kwargs)
        if kind_col is not None:
            user_votes[kind_col] = True
        if cluster_col is not None:
            clusters = self.dataframe("id", index="users")
            user_votes[cluster_col] = clusters
        return user_votes

    def _votes_table_for_clusterization(self):
        # Return votes table with the default parameters used on clusterization
        # jobs.
        return self.votes_table(
            non_classified=True, cluster_col=None, mean_stereotype=True
        )

    def find_clusters(self, pipeline_factory=None):
        """
        Find clusters using the given clusterization pipeline. This method does
        not writes clusters to the database, but rather return the
        clusterization results.

        Args:
            pipeline_factory:
                A function from the number of clusters to Clusterization
                pipeline. The pipeline should receive a dataframe with raw
                voting data, impute values to missing data, normalize and
                classify using stereotype data. Unless you know what you are
                doing it must be constructed with
                :func:`ej_clusters.math.clusterization_pipeline`.

        Returns:
            clusterization (pd.Series):
                A column mapping each user as index to the corresponding
                cluster id.
            pipe (Pipeline):
                A scikit learn Pipeline object that performed the classification
                task.
        """
        pipeline_factory = pipeline_factory or clusterization_pipeline()

        # Check the number of clusters to initialize the pipeline
        n_clusters = self.count()
        if n_clusters == 0:
            log.error("Trying to clusterize empty cluster set.")
            raise ValueError("empty cluster set")
        elif n_clusters == 1:
            log.warning("Creating clusters for cluster set with a single element.")

        # Fetch data and clusterize
        pipe = pipeline_factory(n_clusters)
        votes = self._votes_table_for_clusterization()
        labels = pipe.fit_predict(votes)
        cluster_map = -votes.index[-n_clusters:].values

        # Create result
        labels_ = cluster_map[labels[:-n_clusters]]
        users_ = votes.index[:-n_clusters].values
        series = pd.Series(
            labels_, name="cluster", index=pd.Index(users_, name="users")
        )
        return series, pipe

    def clusterize_from_votes(self, pipeline_factory=None):
        """
        Similar to .find_clusters(), but writes results to the database in an
        atomic transaction.

        Returns:
             The clusterization pipeline object.
        """
        pipeline_factory = pipeline_factory or clusterization_pipeline()
        series, pipe = self.find_clusters(pipeline_factory)
        self.update_membership(series.to_dict())
        return pipe

    def update_membership(self, mapping, by_cluster=False):
        """
        Receives a dictionary of users to clusters and update cluster memberships
        atomically.
        """
        if by_cluster:
            return chain(
                *(
                    ((user, cluster) for user in users)
                    for cluster, users in mapping.items()
                )
            )

        if hasattr(mapping, "items"):
            mapping = mapping.items()

        m2m = self.model.users.through
        links = [
            m2m(
                cluster_id=getattr(cluster, "id", cluster),
                user_id=getattr(user, "id", user),
            )
            for user, cluster in mapping
        ]
        with transaction.atomic():
            m2m.objects.filter(cluster__in=self).delete()
            m2m.objects.bulk_create(links)

    def mean_stereotypes_votes_table(self, data_imputation=None):
        """
        Return a dataframe with the average vote per cluster considering all
        stereotypes in the cluster.
        """
        votes = (
            self.stereotype_votes()
            .annotate(cluster=F.author.clusters)
            .dataframe("author", "comment", "choice", "cluster")
        )

        if votes.shape[0]:
            votes = votes.pivot_table(
                values="choice", index=["author", "cluster"], columns="comment"
            )
        else:
            raise ValueError("no votes found")

        votes["cluster"] = votes.index.get_level_values("cluster")
        votes.index = np.arange(votes.shape[0])
        votes = votes.groupby("cluster").mean()
        return imputation(votes, data_imputation)


class ClusterManager(Manager.from_queryset(ClusterQuerySet)):
    """
    Manage creation and query of cluster objects.
    """

    def create_with_stereotypes(self, name, stereotypes=None, comments=None):
        """
        Creates a new cluster with the given stereotypes.

        If no stereotype is given, creates a single stereotype with the same
        name as the cluster.
        """
        raise NotImplementedError
