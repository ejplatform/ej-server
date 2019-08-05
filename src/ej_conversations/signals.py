from django.dispatch import Signal


#
# Provided signals
#
vote_cast = Signal(providing_args=["vote", "comment", "choice", "is_update", "is_final"])
comment_moderated = Signal(providing_args=["comment", "moderator", "author", "is_approved"])
