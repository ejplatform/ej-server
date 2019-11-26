from django.contrib.auth import get_user_model

from boogie.testing.pytest import CrawlerTester, UrlTester

# from ej_boards.mommy_recipes import BoardRecipes
from ej_clusters.mommy_recipes import ClusterRecipes
from ej_conversations.mommy_recipes import ConversationRecipes
from ej_profiles.mommy_recipes import ProfileRecipes
from ej_users.mommy_recipes import UserRecipes

# TODO: from ej_math.mommy_recipes import MathRecipes
# TODO: from ej_gamification.mommy_recipes import GamificationRecipes
# TODO: from ej_clusterviz.mommy_recipes import ClustervizRecipes
# TODO: from ej_notifications.mommy_recipes import NotificationRecipes
# TODO: from ej_dataviz.mommy_recipes import ReportsRecipes


User = get_user_model()


class DataMixin(
    ClusterRecipes,
    # BoardRecipes,
    ConversationRecipes,
    ProfileRecipes,
    UserRecipes,
):
    def make_user(self, username, **kwargs):
        return User.objects.create_user(name=username, **kwargs)


class Base(DataMixin, CrawlerTester):
    """
    Base crawler for a anonymous user.
    """

    start = "/"
    conversation_url = "/conversations/1/conversation/"
    must_visit = ("/", "/conversations/", conversation_url)


class TestUserCrawl(Base):
    """
    Crawl on all urls accessible by a user without any privileges.
    """

    user = "user"
    must_visit = (*Base.must_visit, "/profile/")


class TestAuthorCrawl(TestUserCrawl):
    """
    Crawl on all urls accessible by the author of a resource.
    """

    user = "author"
    conversation_actions = []
    must_visit = (*TestUserCrawl.must_visit, *[Base.conversation_url + x for x in conversation_actions])


class TestAdminCrawl(TestUserCrawl):
    """
    Crawl on all urls accessible by the admin user resource.
    """

    user = "author"
    must_visit = (*TestAuthorCrawl.must_visit,)


class TestUrls(UrlTester, DataMixin):
    urls = {
        None: Base.must_visit,
        "user": TestUserCrawl.must_visit,
        "author": TestAuthorCrawl.must_visit,
        "admin": TestAdminCrawl.must_visit,
    }
