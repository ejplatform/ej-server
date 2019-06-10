from django.dispatch import Signal


#
# Provided signals
#
vote_cast = Signal(providing_args=["vote", "comment", "choice", "is_update"])
comment_approved = Signal(providing_args=["comment"])
comment_rejected = Signal(providing_args=["comment", "reason"])
