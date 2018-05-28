import sidekick as sk

models = sk.import_later('.models', package=__package__)
powers = sk.deferred(lambda: models.ConversationPowers.objects)


def promote_comment(comment, user=None):
    """
    Promotes a comment.

    If user is given, register that the given user contributed with the
    comment promotion.
    """
    conversation = comment.conversation
    if user:
        powers.incr_by(user, conversation, promote_actions=1)
    if comment.author != user:
        powers.incr_by(comment.author, conversation, promoted_comments=1)
    if not comment.is_promoted:
        comment.is_promoted = True
        comment.save(update_fields=['is_promoted'])
    models.CommentPromotion.objects.get_or_create(user=user, comment=comment)
