from rest_framework.routers import SimpleRouter
from .views import (
    ConversationViewSet,
    CommentViewSet,
    CommentReportViewSet,
    VoteViewSet,
    AuthorViewSet,
)

router = SimpleRouter()
router.register(r'authors', AuthorViewSet), 
router.register(r'conversations', ConversationViewSet)
router.register(r'comments', CommentViewSet)
router.register(r'votes', VoteViewSet)
router.register(r'comments_report', CommentReportViewSet)

urlpatterns = router.urls
