from django.db.models import Case, When


def stereotype_vote_information(
    stereotype, clusterization, conversation, order_option=1, order_direction="-"
):
    if stereotype:
        comments = conversation.comments.approved()

        # Mark stereotypes with information about votes
        stereotype_votes = clusterization.stereotype_votes.filter(author=stereotype)

        if order_option:
            stereotype_votes = order_stereotype_votes_by(stereotype_votes, order_option, order_direction)

        voted = set(vote.comment for vote in stereotype_votes)
        stereotype.non_voted_comments = [x for x in comments if x not in voted]
        stereotype.given_votes = stereotype_votes

        return stereotype


def order_stereotype_votes_by(stereotype_votes, order_option, order_direction):
    choices_values = [0, 1, -1]
    choices_values.remove(int(order_option))
    return stereotype_votes.annotate(
        relevancy=Case(
            When(choice=int(order_option), then=3),
            When(choice=choices_values[0], then=2),
            When(choice=choices_values[1], then=1),
        )
    ).order_by(f"{order_direction}relevancy")


def extract_choice_id(action):
    choice_id = action.split("-")
    return {
        "id": choice_id[1],
        "choice": choice_id[0],
    }
