from django.utils.translation import ugettext as _

TOUR = {
    "i18n": {"next": _("Next"), "dismiss": _("Dismiss")},
    "options": {"defaultStepOptions": {"scrollTo": False, "showCancelLink": True}, "useModalOverlay": True},
    "steps": [
        #
        # Show main interface
        #
        [
            "welcome",
            {"title": _("Welcome to EJ!"), "text": _("Creating a Shepherd is easy too! Just create ...")},
        ],
        [
            "header",
            {
                "title": _("App header"),
                "text": _("This header displays the main actions you can do in each page."),
                "attachTo": ".main-header bottom",
            },
        ],
        [
            "back-button",
            {
                "title": _("App header"),
                "text": _("Like going back to the previous page..."),
                "attachTo": ".main-header a:first-child bottom",
            },
        ],
        [
            "options-menu",
            {
                "title": _("App header"),
                "text": _('... or opening the "options" menu.'),
                "attachTo": ".main-header a:last-child bottom",
            },
        ],
        #
        # Show conversations
        #
        [
            "conversation-card-1",
            {
                "title": _("Conversation Card"),
                "text": _("But here is where the magic starts..."),
                "attachTo": ".conversation-card top",
            },
        ],
        [
            "conversation-card-2",
            {
                "title": _("Conversation Card"),
                "text": _(
                    "Conversations consist questions asked by other users about interesting topics of discussion."
                ),
                "attachTo": ".conversation-card__text bottom",
            },
        ],
        [
            "conversation-card-3",
            {
                "title": _("Conversation Card"),
                "text": _("Click here to join in!"),
                "attachTo": {"element": ".conversation-card__button", "on": "top"},
                "advanceOn": "a click",
                "extra": "foo",
            },
        ],
        #
        # Conversation detail
        #
        [
            "conversation-1",
            {
                "title": _("Conversation"),
                "text": _("Click here to join in!"),
                "attachTo": {"element": ".conversation-ballon", "on": "bottom"},
                "advanceOn": "a click",
            },
        ],
    ],
}
