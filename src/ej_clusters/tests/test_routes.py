from ej.testing import UrlTester
from ej_clusters.mommy_recipes import ClusterRecipes


class TestRoutes(UrlTester, ClusterRecipes):
    user_urls = ["/stereotypes/"]
    owner_urls = ["/conversations/1/conversation/stereotypes/"]
