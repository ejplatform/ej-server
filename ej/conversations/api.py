import ej.conversations.api_views


def register(router):
    router.register(r'conversations', ej.conversations.api_views.ConversationViewSet)
    router.register(r'conversations/authors', ej.conversations.api_views.AuthorViewSet, base_name='authors')
    router.register(r'conversations/comments', ej.conversations.api_views.CommentViewSet, base_name='comments')
    router.register(r'conversations/votes', ej.conversations.api_views.VoteViewSet, base_name='votes')
    router.register(r'conversations/categories', ej.conversations.api_views.CategoryViewSet, base_name='categories')

    router.register(r'conversations/report-comment',
                    ej.conversations.api_views.CommentReportViewSet,
                    base_name='report-comment')
    router.register(r'conversations/next-comment',
                    ej.conversations.api_views.NextCommentViewSet,
                    base_name='next-comment')
    router.register(r'conversations/random-conversation',
                    ej.conversations.api_views.RandomConversationViewSet,
                    base_name='random-conversation')
    router.register(r'conversations/report-conversation',
                    ej.conversations.api_views.ConversationReportViewSet,
                    base_name='report-conversation')
    router.register(r'conversations/conversation-clusters',
                    ej.conversations.api_views.ClusterViewSet,
                    base_name='conversation-clusters')
