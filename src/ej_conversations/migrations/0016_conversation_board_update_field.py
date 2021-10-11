from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("ej_conversations", "0015_add_default_board_to_conversation"),
    ]

    operations = [
        migrations.AlterField(
            model_name="conversation",
            name="board",
            field=models.ForeignKey(
                null=False, blank=False, on_delete=django.db.models.deletion.CASCADE, to="ej_boards.Board"
            ),
        ),
    ]

