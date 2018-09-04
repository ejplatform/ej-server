CATEGORY = {
    'links': {
        'self': 'http://testserver/categories/category/',
    },
    'name': 'Category',
    'slug': 'category',
    'image': None,
    'image_caption': '',
}

USER_ROOT = {
    'url': 'http://testserver/users/root/',
    'username': 'root',
}

USER = {
    'url': 'http://testserver/users/user/',
    'username': 'user',
}

COMMENT = {
    'links': {
        'self': 'http://testserver/comments/1/',
        'author': 'http://testserver/users/comment_author/',
        'conversation': 'http://testserver/conversations/conversation/',
        'vote': 'http://testserver/comments/1/vote',
    },
    'author_name': 'comment_author',
    'content': 'comment',
    'id': 1,
    'rejection_reason': '',
    'statistics': {
        'agree': 0,
        'disagree': 0,
        'missing': 0,
        'skip': 0,
        'total': 0,
    },
    'status': 'APPROVED',
}

CONVERSATION = {
    'links': {
        'self': 'http://testserver/conversations/conversation/',
        'approved_comments': 'http://testserver/conversations/conversation/approved_comments',
        'author': 'http://testserver/users/conversation_author/',
        'category': 'http://testserver/categories/category/',
        'random_comment': 'http://testserver/conversations/conversation/random_comment',
        'user_data': 'http://testserver/conversations/conversation/user_data',
        'votes': 'http://testserver/conversations/conversation/votes',
    },
    'author_name': 'conversation_author',
    'category_name': 'Category',
    'title': 'Conversation',
    'slug': 'conversation',
    'question': 'question?',
    'is_promoted': False,
    'statistics': {
        'comments': {
            'approved': 0, 'rejected': 0, 'pending': 0, 'total': 0,
        },
        'votes': {
            'agree': 0, 'disagree': 0, 'skip': 0, 'total': 0,
        },
        'participants': 0,
    },
}

VOTE = {
    'links': {
        'comment': 'http://testserver/comments/1/',
        'self': 'http://testserver/votes/1/',
    },
    'action': 'agree', 'comment_text': 'comment',
}
