"""
A few functions for creating plausible synthetic data.
"""
from random import choice, random

from django.contrib.auth import get_user_model
from django.db.models import Model
from faker import Factory

from ... import create_conversation
from ...models import Comment

fake = Factory.create()
User = get_user_model()


class ExampleData:
    def __init__(self, users, verbose):
        self.users = list(users)
        self.staff_users = [x for x in self.users if x.is_staff]
        self.verbose = verbose
        if verbose:
            self.log = (lambda x: 'Created: %s' % x)
        else:
            self.log = (lambda x: None)

    def __setattr__(self, key, value):
        if isinstance(value, Model):
            self.log(value)
        super().__setattr__(key, value)

    def _comment_factory(self, conversation):
        create = conversation.create_comment
        return (
            lambda comment, status='approved': create(
                self.get_user(),
                comment,
                check_limits=False,
                status=status)
        )

    def make_conversations(self):
        self.better_language = create_conversation(
            'We want to create the best programming language. How should it be?',
            'A better programming language',
            self.get_staff_user(),
            is_promoted=True,
        )
        self.school_system = create_conversation(
            'How can we improve the schools and education in our community?',
            'School system',
            self.get_staff_user(),
            is_promoted=True,
        )
        self.participation = create_conversation(
            'How can we make our democracy more participative?',
            'Participative democracy',
            self.get_staff_user(),
            is_promoted=True,
        )

    def make_language_comments(self):
        new = self._comment_factory(self.better_language)
        new('It must be functional to control side-effects.')
        new('I want a purely OO language.')
        new('We have Python! We don\'t need a new language!')
        new('It has to run on the browser.')
        new('It must be really fast.')
        new('I want a statically typed language.')
        new('It must be dynamic, but accept type hints.',
            status='pending')

    def make_school_comments(self):
        new = self._comment_factory(self.school_system)
        new('We need more arts and crafts lessons.')
        new('We have to encourage the use technology and teach programming.')
        new('Our curriculum should be open and focused on real problems.')
        new('Students should have a say on what they want to learn.')
        new('We don\'t need no education! We don\'t need no thought control!',
            status='pending')

    def make_democracy_comments(self, extra=50):
        new = self._comment_factory(self.participation)
        new('People should have direct power to decide community affairs.')
        new('We need to forbid corporations from financing elections.')
        new('We need better voting systems.', status='pending')
        for _ in range(extra):
            new(fake.paragraph())

    def make_votes(self):
        comments = list(Comment.approved.all())
        probs = [(x, (random(), random(), random() / 3)) for x in comments]
        for comment, probs in probs:
            for user in self.users:
                self.random_vote(comment, user, probs)

    def random_vote(self, comment, user, probs):
        p_vote, p_skip, p_ok = probs
        if random() < p_vote:
            if random() < p_skip:
                comment.vote(user, 'skip')
            elif random() < p_ok:
                comment.vote(user, 'agree')
            else:
                comment.vote(user, 'disagree')

    def make_all(self):
        self.make_conversations()
        self.make_language_comments()
        self.make_school_comments()
        self.make_democracy_comments()
        self.make_votes()

    def get_staff_user(self):
        return choice(self.staff_users)

    def get_user(self):
        return choice(self.users)


def make_examples(users=None, verbose=False):
    """
    Takes a list of users and creates plausible synthetic data.
    """
    if users is None:
        users = User.objects.all()

    data = ExampleData(users, verbose)
    data.make_all()
