import json
from boogie.router import Router
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponse
from .opinion_component.aquisition import AquisitionService
from ej_conversations import models
import datetime
from django.http import JsonResponse

app_name = "ej_analysis"
urlpatterns = Router(
    template="ej_conversations_analysis/{name}.jinja2", models={"conversation": models.Conversation}
)
conversation_analysis_url = f"<model:conversation>/<slug:slug>/analysis"
conversation_analysis_url_aquisition_viz = f"<model:conversation>/<slug:slug>/analysis/aquisition_viz"


@urlpatterns.route(conversation_analysis_url)
def index(request, conversation, slug):
    return {"conversation": conversation}


@urlpatterns.route(conversation_analysis_url_aquisition_viz)
def aquisition(request, conversation, slug):
    start_date = datetime.date.fromisoformat(request.GET.get("startDate"))
    end_date = datetime.date.fromisoformat(request.GET.get("endDate"))
    view_id = request.GET.get("viewId")
    authors = (
        conversation.votes.filter(created__range=[start_date, end_date])
        .order_by("author")
        .distinct("author")
    )
    aquisition_service = AquisitionService(start_date, end_date, view_id, authors)
    return JsonResponse(aquisition_service.d3js_data())
