from ej_clusters.mommy_recipes import ClusterRecipes


class TestBasicAPI(ClusterRecipes):
    def test_related_fields(self, conversation):
        assert conversation.stereotypes
        assert conversation.get_clusterization


class TestClusterization(ClusterRecipes):
    def test_inject_clusters_related_manager_on_conversation(self, conversation_db):
        conversation_db.get_clusterization()
        assert hasattr(conversation_db.clusterization, 'clusters')
        assert hasattr(conversation_db, 'clusters')

    def test_clusterization_str_method(self, clusterization, conversation):
        assert str(clusterization) == f'{conversation} (0 clusters)'
        assert clusterization.get_absolute_url() == f'{conversation.get_absolute_url()}clusters/'


class TestCluster(ClusterRecipes):
    def test_cluster_str_method(self, cluster, conversation):
        cluster.id = 42
        assert f'cluster ("{conversation}" conversation)' == str(cluster)
        assert cluster.get_absolute_url() == f'{conversation.get_absolute_url()}clusters/42/'
