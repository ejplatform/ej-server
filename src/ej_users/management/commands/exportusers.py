from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

User = get_user_model()


class Command(BaseCommand):
    help = "Export users data in a csv file"

    def handle(self, *files, **options):
        with open("users.csv", "w") as csv:
            csv.write("id, name, email, last_login,\n")
            for user in User.objects.all():
                line = ", ".join([user.id, user.name, user.email, user.last_login])
                csv.write(line + "\n")
