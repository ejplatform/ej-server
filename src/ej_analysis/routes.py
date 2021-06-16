import json
from boogie.router import Router
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponse
from .opinion_component.lib.analytics_wrapper import AnalyticsWrapper
from .opinion_component.lib.mongodb_wrapper import MongodbWrapper
from .opinion_component.lib.d3js_wrapper import D3jsWrapper
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
    analytics_wrapper = AnalyticsWrapper(start_date, end_date, view_id)
    mongodb_wrapper = MongodbWrapper()
    aquisition = mongodb_wrapper.get_page_aquisition()
    print("aquisition")
    print(aquisition)
    print("aquisition")
    engajement = analytics_wrapper.get_page_engajement()
    d3js_wrapper = D3jsWrapper(aquisition, engajement)
    return JsonResponse(d3js_wrapper.get_data())
