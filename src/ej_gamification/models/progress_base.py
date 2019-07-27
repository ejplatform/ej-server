from boogie import models
from django.utils.translation import ugettext_lazy as _
from sidekick import lazy, import_later

from .progress_queryset import ProgressQuerySet

signals = import_later("..signals", package=__package__)


class ProgressBase(models.Model):
    """
    Common features of all Progress models.
    """

    score = models.PositiveSmallIntegerField(_("score"), default=0)
    score_bias = models.SmallIntegerField(
        _("score adjustment"), default=0, help_text=_("Artificially increase score for any reason")
    )
    objects = ProgressQuerySet.as_manager()

    @classmethod
    def level_fields(cls):
        try:
            return cls.__dict__["_level_fields"]
        except KeyError:
            fields = {}
            for field in cls._meta.fields:
                if field.name.endswith("_level") and not field.name.startswith("max_"):
                    fields[field.name[:-6]] = field.enum
            setattr(cls, "_level_fields", fields)
            return fields

    @property
    def level_achievement_signal(self):
        raise NotImplementedError("must be defined in subclass")

    @lazy
    def position(self):
        return len(type(self).objects.order_by("-score").filter(score__gt=self.score))

    class Meta:
        abstract = True

    def sync(self):
        self.score = self.compute_score()
        self.update_levels(commit=False)
        return self

    def sync_and_save(self):
        self.sync()
        self.save()
        return self

    def update_level(self, name, commit=True):
        """
        Update given level and possibly save modification, if necessary.

        Return True, if level was changed and False otherwise.
        """
        level_attr = name + "_level"
        max_level_attr = f"max_{name}_level"

        current = getattr(self, level_attr)
        new_level = current.check_level(self)
        max_level = getattr(self, max_level_attr)

        if new_level != current:
            update_fields = [level_attr]
            setattr(self, level_attr, new_level)
            if new_level > max_level:
                setattr(self, max_level_attr, new_level)
                update_fields.append(max_level_attr)

            self.notify_achievement(new_level, name, new_level > current)

            if commit:
                self.save(update_fields=update_fields)
            return True

        return False

    def update_levels(self, commit=True):
        """
        Update all levels in model.

        Return a list with all updated levels.
        """

        updated = []
        for name in self.level_fields():
            if self.update_level(name, commit=False):
                updated.append(name)

        if commit and updated:
            fields = [*(f"{name}_level" for name in updated), *(f"max_{name}_level" for name in updated)]
            self.save(update_fields=fields)

        return updated

    def compute_score(self):
        """
        Return score computed from user achievements.
        """
        raise NotImplementedError("must be implemented in subclass")

    def notify_achievement(self, level, track, is_improvement):
        """
        Send the proper signal to notify a new user achievement.
        """
        signal = self.level_achievement_signal
        args = {"progress": self, "level": level, "track": track, "is_improvement": is_improvement}
        if "user" in signal.providing_args:
            args["user"] = self.user
        if "conversation" in signal.providing_args:
            args["conversation"] = self.conversation
        return signal.send_robust(type(self), **args)


def get_participation(user, conversation, sync=False):
    """
    Return a valid ParticipationProgress() for user.
    """
    progress, created = user.participation_progresses.get_or_create(conversation=conversation)
    if created:
        progress.sync().save()
        return progress
    if sync:
        progress.sync().save()
    return progress


def get_progress(obj, sync=False):
    """
    Return a valid ConversationProgress() or UserProgress() for object.
    """
    from ej_conversations.models import Conversation

    try:
        progress = obj.progress
    except AttributeError:
        if isinstance(obj, Conversation):
            from .progress_conversation import ConversationProgress

            progress = ConversationProgress(conversation=obj).sync()
        else:
            from .progress_user import UserProgress

            progress = UserProgress(user=obj).sync()
        progress.save()
        return progress

    if sync:
        progress.sync().save()
    return progress
