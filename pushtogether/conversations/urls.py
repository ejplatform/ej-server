from rest_framework.routers import SimpleRouter
from .views import (
    ConversationViewSet,
    ConversationReportViewSet,
    CommentViewSet,
    NextCommentViewSet,
    CommentReportViewSet,
    VoteViewSet,
    AuthorViewSet,
    RandomConversationViewSet
)
from django.conf.urls import url

router = SimpleRouter()
router.register(r'authors', AuthorViewSet)
router.register(r'conversations', ConversationViewSet, base_name='conversation')
router.register(r'comments', CommentViewSet)
router.register(r'votes', VoteViewSet)
router.register(r'conversations-report', ConversationReportViewSet,
                base_name='conversation-report')
router.register(r'comments-report', CommentReportViewSet,
                base_name='comment-report')
router.register(r'next_comment', NextCommentViewSet,
                base_name='conversation-next-comment')

urlpatterns = [
    url(
        regex=r'^random-conversation/$',
        view=RandomConversationViewSet.as_view({'get': 'retrieve'}),
        name='random-conversation'
    ),
]

urlpatterns.extend(router.urls)
