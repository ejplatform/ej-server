from django.db import migrations
from django.db import transaction
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _


def user_not_have_default_board(user):
    default_board = (slugify(user.email[:50]),)
    return not (default_board in list(user.boards.values_list("slug")))


def get_or_create_user_default_board(user, db_alias, Boards):
    default_board = None
    if user_not_have_default_board(user):
        try:
            with transaction.atomic():
                default_board = Boards.objects.using(db_alias).create(
                    slug=slugify(user.email[:50]),
                    owner=user,
                    title=_("My Board"),
                    description="Default user board",
                    palette="brand",
                )
            return default_board
        except Exception as e:
            print(e)
    return Boards.objects.using(db_alias).get(slug=slugify(user.email[:50]))


def add_default_board(apps, schema_editor):
    db_alias = schema_editor.connection.alias
    Boards = apps.get_model("ej_boards", "Board")
    Conversation = apps.get_model("ej_conversations", "Conversation")
    user_default_board = None

    for conversation in Conversation.objects.all():
        with transaction.atomic():
            conversation_author = conversation.author
            user_default_board = get_or_create_user_default_board(conversation_author, db_alias, Boards)
            try:
                board = getattr(conversation, "board")
                if board == None:
                    conversation.board = user_default_board
                    conversation.save()
            except Exception as e:
                conversation.board = user_default_board
                conversation.save()


class Migration(migrations.Migration):

    dependencies = [
        ("ej_boards", "0005_remove_board_conversations"),
        ("ej_conversations", "0014_conversation_board"),
    ]

    operations = [migrations.RunPython(add_default_board)]
