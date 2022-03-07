from ej_clusters.mommy_recipes import ClusterRecipes


class TestClusterization(ClusterRecipes):
    def test_inject_clusters_related_manager_on_conversation(self, conversation_db):
        conversation_db.get_clusterization()
        assert hasattr(conversation_db.clusterization, "clusters")
        assert hasattr(conversation_db, "clusters")

    def test_clusterization_str_method(self, clusterization):
        conversation = clusterization.conversation
        conversation.id = 1
        assert str(clusterization) == f"{conversation} (0 clusters)"
        assert f"{clusterization.get_absolute_url()}" == f"{conversation.get_absolute_url().url}clusters/"
