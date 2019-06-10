import dramatiq

from .models import Clusterization


@dramatiq.actor
def update_clusterization(id):
    """
    Task that fetches a clusterization with the given id and executes it's
    .update_clusterization() method.
    """
    clusterization = Clusterization.objects.filter(id=id).first()
    if clusterization is not None:
        clusterization.update_clusterization()
