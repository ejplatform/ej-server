from django.shortcuts import redirect

from boogie.router import Router
from ej_clusters.forms import StereotypeForm
from ej_clusters.utils import check_stereotype
from .models import Stereotype

app_name = "ej_cluster"
urlpatterns = Router(
    template="ej_clusters/stereotypes/{name}.jinja2", models={"stereotype": Stereotype}, login=True
)


@urlpatterns.route("")
def list(request, **kwargs):
    qs = request.user.stereotypes.prefetch_related("clusters__clusterization__conversation")
    stereotypes = []
    for stereotype in qs:
        stereotype.conversations = conversations = []
        for cluster in stereotype.clusters.all():
            conversations.append(cluster.clusterization.conversation)
        stereotypes.append(stereotype)
    return {"stereotypes": stereotypes}


@urlpatterns.route("add/")
def create(request, **kwargs):
    form = StereotypeForm(request=request, owner=request.user)
    if form.is_valid_post():
        form.save()
        return redirect("stereotypes:list")
    return {"form": form}


@urlpatterns.route("<model:stereotype>/edit/")
def edit(request, stereotype, **kwargs):
    check_stereotype(stereotype, request.user)
    form = StereotypeForm(request=request, instance=stereotype)

    if request.POST.get("action") == "delete":
        stereotype.delete()
        return redirect("stereotypes:list")
    elif form.is_valid_post():
        form.save()
        return redirect("stereotypes:list")
    return {"form": form, "stereotype": stereotype}
