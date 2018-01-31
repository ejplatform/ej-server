from rest_framework.routers import SimpleRouter

from django.conf.urls import url

from . import views

router = SimpleRouter()
router.register(
    r'authors',
    views.AuthorViewSet
)
router.register(
    r'conversations',
    views.ConversationViewSet,
    base_name='conversation'
)
router.register(
    r'comments',
    views.CommentViewSet
)
router.register(
    r'votes',
    views.VoteViewSet
)
router.register(
    r'conversations-report',
    views.ConversationReportViewSet,
    base_name='conversation-report'
)
router.register(
    r'comments-report',
    views.CommentReportViewSet,
    base_name='comment-report'
)
router.register(
    r'next_comment',
    views.NextCommentViewSet,
    base_name='conversation-next-comment'
)
router.register(
    r'conversation-clusters',
    views.ClustersViewSet,
    base_name='conversation-clusters'
)

urlpatterns = [
    url(
        regex=r'^random-conversation/$',
        view=views.RandomConversationViewSet.as_view({'get': 'retrieve'}),
        name='random-conversation'
    ),
]

urlpatterns.extend(router.urls)
