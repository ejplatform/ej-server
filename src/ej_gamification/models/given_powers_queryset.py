from polymorphic.managers import PolymorphicQuerySet


class GivenPowerQuerySet(PolymorphicQuerySet):
    def incr_by(self, user, conversation, **kwargs):
        """
        Increment the given numeric powers/achievements by the given quantity.
        """
        self.get_powers(user, conversation)

    def incr_all_by(self, **kwargs):
        """
        Increment all values in the current queryset by the given amount.
        """
        raise NotImplementedError

    def get_powers(self, user, conversation):
        """
        Return the ConversationPower instance for user in conversation
        """
        return self.get_or_create(user=user, conversation=conversation)[0]

    def has_powers(self, user, conversation):
        """
        Return True if user has any powers in the given conversation.
        """
        try:
            powers = self.get(user=user, conversation=conversation)
        except self.model.DoesNotExist:
            return False
        else:
            return powers.has_powers
