from random import choice, random, randint, shuffle

from boogie.models import QuerySet
from django.db import transaction
from faker import Factory

from ej_conversations import Choice
from ej_conversations.models import Conversation, Comment, Vote
from ej_profiles.enums import Gender, Race
from ej_profiles.models import Profile
from ej_users.models import User

fake = Factory.create()

# Create genders and make try to increase the probabilities of MALE and FEMALE
# attributions if they likely exist.
GENDERS = list(Gender)
if len(GENDERS) > 3:
    GENDERS += 3 * GENDERS[1:3]

# Create races and increase the probability of the first 3 races.
RACES = list(Race)
if len(RACES) > 3:
    RACES += 3 * RACES[1:3]

COMMENT_STATUS = [Comment.STATUS.approved] * 4 + [Comment.STATUS.rejected, Comment.STATUS.pending]
RANDOM_PROFILE_FIELDS = {
    "race": lambda: choice(RACES),
    "gender": lambda: choice(GENDERS),
    "birth_date": fake.date_of_birth,
    "country": fake.country,
    "state": fake.state,
    "city": fake.city,
    "biography": fake.paragraph,
    "occupation": fake.job,
    "political_activity": fake.paragraph,
}


#
# Create users
#
def create_users(n, fill_profile=True):
    """
    Create n random new users.
    """

    ids = User.objects[:, "id"]
    User.objects.bulk_create([User(name=fake.name(), email=fake.email()) for _ in range(n)])
    user_ids = User.objects.exclude(id__in=ids)

    if fill_profile:
        Profile.objects.bulk_create(random_profile(user) for user in user_ids)


def random_profile(user, prob=0.33):
    """
    Create random profile for user.
    """

    items = RANDOM_PROFILE_FIELDS.items()
    fields = {k: v() for k, v in items if random() <= prob}
    return Profile(user_id=user.id, **fields)


#
# Create conversations
#
def create_conversations(n, n_comments):
    """
    Create n random conversations with n_comments comments each.
    """

    users = User.objects.all()
    for _ in range(n):
        create_conversation(users, n_comments)


def create_conversation(users, n_comments):
    """
    Create a conversation with n_comments comments involving the users in
    the given queryset.
    """

    with transaction.atomic():
        conversation = Conversation.objects.create(
            title=fake.catch_phrase(),
            text=fake.catch_phrase() + "?",
            author=users.random(),
            slug=fake.slug(),
            is_promoted=choice([True, False]),
        )
        conversation.moderators.set([users.random() for _ in range(randint(0, 5))])

        for comment in range(n_comments):
            Comment.objects.create(
                status=choice(COMMENT_STATUS),
                conversation=conversation,
                author=users.random(),
                content=fake.paragraph(),
                rejection_reason_text=fake.paragraph(),
            )
    return conversation


#
# Votes in conversation
#
def random_votes(n, conversation, users=None, n_users=None, bias=0.7, skip=0.333, miss=0.5, profile=None):
    """
    Create an average of n random votes per comment in the given conversation.
    """
    users = random_voters_for_conversation(n_users, conversation, users)
    votes = []
    profile = profile or {}

    for comment in conversation.comments.distinct():
        voters = as_queryset(users, User).exclude(votes__comment=comment)
        miss_, skip_, bias_ = profile.get(comment, (miss, skip, bias))
        m = n / miss_
        has_voted = set()

        for author in voters.order_by("?").distinct()[0:m]:
            if author.id in has_voted or random() < miss_:
                continue

            vote = random_choice(skip_, bias_)
            votes.append(Vote(comment=comment, author=author, choice=vote))
            has_voted.add(author.id)

    return Vote.objects.bulk_create(votes)


def random_voting_profile(comments):
    return {comment: (random(), random() * 0.666, random()) for comment in comments}


def random_voters_for_conversation(n, conversation, users=None):
    authors = conversation.comments.authors()
    extra = as_queryset(users or User.objects.all(), User)
    return (authors | extra.order_by("?")[: n - len(authors)]).distinct()


def partition_voters(n, users):
    users = list(users)
    shuffle(users)
    return [users[start::n] for start in range(n)]


def as_queryset(obj, model):
    if isinstance(obj, QuerySet):
        return obj
    else:
        return model.objects.filter(pk__in=(x.pk for x in obj))


def random_choice(skip, bias):
    if random() <= skip:
        return Choice.SKIP
    elif random() < bias:
        return Choice.AGREE
    else:
        return Choice.DISAGREE
