from boogie import models
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist


class FavoriteConversation(models.Model):
    """
    M2M relation from users to conversations.
    """

    conversation = models.ForeignKey("Conversation", on_delete=models.CASCADE, related_name="favorites")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="favorite_conversations"
    )


class HasFavoriteMixin:
    """
    Mixin class for model that has a reference to a favorites relationship.
    """

    favorites = NotImplemented

    def is_favorite(self, user):
        """
        Checks if conversation is favorite for the given user.
        """
        return bool(self.favorites.filter(user=user).exists())

    def make_favorite(self, user):
        """
        Make conversation favorite for user.
        """
        self.favorites.update_or_create(user=user)

    def remove_favorite(self, user):
        """
        Remove favorite status for conversation
        """
        if self.is_favorite(user):
            self.favorites.filter(user=user).delete()

    def toggle_favorite(self, user):
        """
        Toggles favorite status of conversation.

        Return the final favorite status.
        """
        try:
            self.favorites.get(user=user).delete()
            return False
        except ObjectDoesNotExist:
            self.make_favorite(user)
            return True
