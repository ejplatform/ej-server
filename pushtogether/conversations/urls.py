from rest_framework.routers import SimpleRouter
from .views import (
    ConversationViewSet,
    ConversationReportViewSet,
    CommentViewSet,
    CommentReportViewSet,
    VoteViewSet,
    AuthorViewSet,
)

router = SimpleRouter()
router.register(r'authors', AuthorViewSet), 
router.register(r'conversations_report', ConversationReportViewSet)
router.register(r'comments_report', CommentReportViewSet)
router.register(r'conversations', ConversationViewSet)
router.register(r'comments', CommentViewSet)
router.register(r'votes', VoteViewSet)

urlpatterns = router.urls
