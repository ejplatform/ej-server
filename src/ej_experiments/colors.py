from random import random

import numpy as np
from django.db import IntegrityError
from sidekick import import_later

global_id = 0
get_user_model = import_later("django.contrib.auth:get_user_model")


def create_colors_experiment(skip_prob=0.25, n_times=1, n_users=21, has_yellow=False):
    """
    The "colors" experiment creates a few groups tagged by color names.
    Each comment has a baseline probability of around 25% for agree/disagree in
    the general population, but has some different probability for each user.
    """
    from ej_conversations import create_conversation
    from ej_clusters.models import Clusterization
    from ej_clusters.enums import ClusterStatus

    # Conversation
    rgb = ("red", "green", "blue")
    author = create_user("color", "admin")
    conversation = create_conversation("What is your favorite color?", "Color", author, is_promoted=True)

    # Create users
    colors = (*rgb, "yellow") if has_yellow else rgb
    user_map = {color: users(color, n_users) for color in colors}

    # Create comments
    comment_map = {
        color: repeat(n_times, comments, color, user_map[color][0], conversation) for color in rgb
    }

    # Cast votes for users and stereotypes
    clusterization = Clusterization.objects.create(
        conversation=conversation, cluster_status=ClusterStatus.ACTIVE
    )
    votes = cast_user_votes(comment_map, user_map, skip_prob)
    stereotype_votes = cast_stereotypes_votes(comment_map, clusterization)
    votes.extend(stereotype_votes)
    clusterization.update_clusterization(force=True)
    return votes


def cast_user_votes(comment_map, user_map, skip_prob):
    """
    Return a list of user votes.

    Args:
        comment_map:
            map from colors to a list of comments
        user_map:
            map from colors to a list o users
        skip_prob:
            probability of not voting
    """
    from ej_conversations.models import Vote

    # Cast votes
    votes = []
    for c_color, c_list in comment_map.items():
        for comment in c_list:
            for u_color, u_list in user_map.items():
                for user in u_list:
                    if random() > skip_prob:
                        prob = 0.25
                        if u_color == "yellow":
                            if comment.group == "red":
                                a = user.idx / 10
                                b = 1 - a
                                prob = a * comment.prob + b * prob
                            elif comment.group == "green":
                                b = user.idx / 10
                                a = 1 - b
                                prob = a * comment.prob + b * prob
                        elif user.group == comment.group:
                            prob = comment.prob

                        choice = "agree" if random() <= prob else "disagree"
                        votes.append(comment.vote(user, choice, False))
    print(f"{len(votes)} votes")
    return Vote.objects.bulk_create(votes)


def cast_stereotypes_votes(comment_map, clusterization):
    """
    Return a list of user votes.

    Args:
        comment_map:
            map from colors to a list of comments
        clusterization:
            a clusterization object
    """
    from ej_clusters.models import Stereotype, Cluster, StereotypeVote

    rgb = ("red", "green", "blue")
    author = clusterization.owner

    # Create personas and votes
    stereotype_votes = []
    commit = True
    yellow_clusters = []
    for color in rgb:
        cluster = Cluster.objects.create(name=color, clusterization=clusterization)
        stereotype, _ = Stereotype.objects.get_or_create(name=color, owner=author)
        cluster.stereotypes.add(stereotype)
        if color in ("red", "green"):
            yellow_clusters.append(cluster)

        for comment in comment_map[color]:
            choice = "agree" if 0.5 < comment.prob else "disagree"
            vote = stereotype.vote(comment, choice, commit)
            stereotype_votes.append(vote)

    # # Add yellow stereotype
    # yellow_stereotype, _ = Stereotype.objects.get_or_create(name='yellow', owner=author)
    # for cluster in yellow_clusters:
    #     cluster.stereotypes.add(yellow_stereotype)
    #
    #     for color in ('red', 'green'):
    #         for comment in comment_map[color]:
    #             prob = comment.prob * 0.5 + 0.25
    #             choice = 'agree' if random() < prob else 'disagree'
    #             vote = yellow_stereotype.vote(comment, choice, commit)
    #             stereotype_votes.append(vote)

    if not commit:
        stereotype_votes = StereotypeVote.objects.bulk_create(stereotype_votes)
    return stereotype_votes


def users(name, n_users=10):
    """
    Return a list of users
    """
    return [create_user(name, i) for i in np.linspace(0, 10, n_users)]


def create_user(group, idx, **kwargs):
    """
    Create a new user with given name/index.
    """
    create = get_user_model().objects.create_user
    name = f"{group}-{idx}"
    email = f"{name}@colors.com"
    try:
        user = create(email, "{name}", name=name, **kwargs)
    except IntegrityError:
        user = get_user_model().objects.get(email=email)
    user.idx = idx
    user.group = group
    return user


def comments(group, author, conversation):
    """
    Return a list of comments
    """
    global global_id
    from ej_conversations.models import Comment

    last_pk = getattr(Comment.objects.order_by("id").last(), "id")
    Comment.objects.bulk_create(
        [
            Comment(
                status=Comment.STATUS.approved,
                author=author,
                content=f"{group.title()}/({global_id}) - {n}%",
                conversation=conversation,
            )
            for n in [0, 2, 5, 10, 50, 75, 90, 95, 98, 100]
        ]
    )
    global_id += 1

    result = []
    if last_pk is None:
        comments = Comment.objects.all()
    else:
        comments = Comment.objects.filter(id__gt=last_pk)

    for comment in comments:
        comment.group = group
        comment.prob = int(comment.content.split(" - ")[-1].strip("%")) / 100
        result.append(comment)
    return result


def repeat(n_times, func, *args, **kwargs):
    results = []
    for _ in range(n_times):
        results.extend(func(*args, **kwargs))
    return results


if __name__ == "__main__":
    from ej.run import run

    run(create_colors_experiment)
