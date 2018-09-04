REPORT_RESPONSE = {
    'statistics':
        {'votes':
            {'agree': 0, 'disagree': 0, 'skip': 0, 'total': 0},
            'comments':
                {'approved': 0, 'rejected': 0, 'pending': 0, 'total': 0},
            'participants': 0},
}


CSV_OUT = {
    'votes_header': 'user,comment,choice',
    'votes_content': '0,0,0',
    'comments_header': 'author,text,agree,disagree,skipped,divergence,participation',
    'comments_content': '0,0,0,0,0,0,0',
    'user_header': 'name,agree,disagree,skipped,divergence',
}

MAP_TO_TABLE = [['agree', 'disagree', 'skip', 'total'], ['0', '0', '0', '0']]
