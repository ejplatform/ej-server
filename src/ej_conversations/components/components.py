from django.utils.translation import ugettext_lazy as _

from hyperpython import div, b, span, p, form, input_, ul, li, h3, textarea


def comment_moderation(request, comment):
    return div(class_='Comment')[
        div(class_='Comment-metadata')[
            span(_('by: ')),
            b(comment.author.name),
            span(comment.created.strftime('%d-%m-%Y %Hh%M'), class_='date'),
        ],
        p(comment.content),
        form(method='post')[
            request.csrf_input,
            input_(type='hidden', name='comment', value=str(comment.id)),
            ul(class_='ConversationComment-actions')[
                li(up_expand=True)[
                    input_(type='submit', class_='Button', name='vote', value='approve'),
                    span(_('Approve')),
                ],
                li(up_expand=True)[
                    input_(type='submit', class_='Button', name='vote', value='disapprove',
                           onclick="var $r = $('#Comment-{{comment.id}}-rejection_reason'); return $r.is(':visible') ? true : $r.show() && false'"),
                    span(_('Disapprove')),
                ]
            ],
            div(id=f'Comment-{comment.id}-rejection_reason',
                class_='Comment-rejection', style='display: none;')[
                h3(_('Reason')),
                p(_('The comment will receive your rejection reason')),
                textarea(
                    name='rejection_reason',
                    id=f'Comment-{comment.id}-rejection_reason',
                    placeholder=_(
                        "Example: Dear user, your comment was rejected "
                        "because it contains discriminatory content."
                    )),
                input_(type='submit', class_='Button', name='vote', value='disapprove'),
            ]
        ]
    ]
