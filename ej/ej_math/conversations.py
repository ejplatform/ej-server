import io

import numpy as np
from django.db import models


class ConversationTask(models.Model):
    """
    Task with a reference to a Conversation.
    """
    object = models.ForeignKey(
        'ej_conversations.Conversation',
        related_name="tasks",
        on_delete=models.CASCADE,
    )
    result = models.BinaryField(blank=True)

    def wrap_result(self, result):
        data = io.BytesIO()

        labels, centroids = result
        labels_data = labels.tobytes()
        centroids_data = centroids.tobytes()

        data.write(bytes(str(len(labels_data))) + b'\n')
        data.write(labels_data)
        data.write(centroids_data)

        return data.getvalue()

    def unwrap_result(self, raw):
        size, _, raw = raw.partition(b'\n')
        labels_data, centroids_data = raw[:size], raw[size:]
        labels = np.fromstring(labels_data, dtype=int)
        centroids = np.fromstring(centroids_data, dtype=float)
        print(labels)
        print(labels.shape)
        print(centroids)
        print(centroids.shape)
        return labels, centroids

# @task(ConversationTask)
# def clusterize(conversation):
#     votes, stereotypes = get_votes_with_stereotypes(conversation)
#     return kmeans_stereotypes(votes, stereotypes)
#
# @task(ConversationTask)
# def compute_distances(obj):
#     pass
#
#
# @receiver(post_save, sender=Vote)
# def vote(sender, instance=None, **kwargs):
#     conversation = instance.comment.conversation
#     clusterize.schedule(conversation)
