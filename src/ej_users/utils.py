from random import choice

from faker import Factory
from django.db.utils import DatabaseError

fake = Factory.create('pt-BR')

ADJECTIVES = [
    'grumpy', 'happy', 'cute', 'smart', 'witty', 'quick'
]


def random_name(fmt='{adjective} {noun}'):
    for _iter in range(100):
        name = fmt.format(adjective=get_adjective(), noun=get_noun())
        if not name_exists(name):
            return name
    else:
        raise RuntimeError(
            'maximum number of attempts reached when trying to generate a '
            'unique random name'
        )


def get_noun():
    return fake.name()


def get_adjective():
    return choice(ADJECTIVES)


def name_exists(name):
    from .models import User

    try:
        return User.objects.filter(display_name=name).exists()
    except DatabaseError:
        return False
