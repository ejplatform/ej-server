from random import random

from sidekick import import_later

global_id = 0
get_user_model = import_later("django.contrib.auth:get_user_model")


def create_clusters(k=3, n_users=20, n_comments=50, missing=0.0, fraction=0.5):
    """
    Create clusters that have ideally placed stereotypes.
    """
    from ej_clusters.math.factories import random_clusterization
    from ej_conversations import create_conversation
    from ej_conversations.models import Vote
    from django.contrib.auth import get_user_model
    from django.db.transaction import atomic

    votes, centroids = random_clusterization([n_users] * k, n_comments, alpha=0.5, missing=missing)

    # Save to database
    with atomic():
        author = get_user_model().objects.filter(is_active=True).last()
        users = list(get_user_model().objects.filter(is_active=True)[: (n_users * k)])
        conversation = create_conversation("What?", "what", author, is_promoted=True)

        comments = []
        for n in range(n_comments):
            comment = conversation.create_comment(author, f"Comment {n + 1}", check_limits=False)
            comments.append(comment)

        clusterization = conversation.get_clusterization()
        for m in range(k):
            cluster = clusterization.clusters.create(name=f"Cluster-{m + 1}")
            stereotype = cluster.stereotypes.create(
                name=f"Persona for cluster {m + 1}/{conversation.id}", owner=author
            )
            for n, comment in enumerate(comments[: int(fraction * n_comments)]):
                stereotype.vote(comment, 1 if random() < centroids[m, n] else -1)

        db_votes = []
        for i, user in enumerate(users):
            for j, comment in enumerate(comments):
                choice = votes[i, j]
                if choice:
                    vote = comment.vote(user, choice, commit=False)
                    db_votes.append(vote)

        Vote.objects.bulk_create(db_votes)
        clusterization.update_clusterization(force=True)

        # Check correctness
        # py_votes = pd.DataFrame(votes, index=[u.id for u in users], columns=[c.id for c in comments])
        # db_votes = conversation.comments.votes_table()
        # assert ((db_votes - py_votes) == 0).all()

    return conversation


if __name__ == "__main__":
    from ej.run import run

    print("...")
    run(create_clusters)
