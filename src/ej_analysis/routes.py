import json
from boogie.router import Router
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponse
from .opinion_component.lib.analytics_wrapper import AnalyticsWrapper
from .opinion_component.lib.mongodb_wrapper import MongodbWrapper
from .opinion_component.lib.d3js_wrapper import D3jsWrapper
from .opinion_component.lib.airflow_client import AirflowClient
from ej_conversations import models
import datetime
from django.http import JsonResponse

app_name = "ej_analysis"
urlpatterns = Router(
    template="ej_conversations_analysis/{name}.jinja2", models={"conversation": models.Conversation}
)
conversation_analysis_url = f"<model:conversation>/<slug:slug>/analysis"
conversation_analysis_url_aquisition_viz = f"<model:conversation>/<slug:slug>/analysis/aquisition_viz"
conversation_analysis_url_aquisition_viz_start_collect = (
    f"<model:conversation>/<slug:slug>/analysis/aquisition_viz_data_collect"
)


@urlpatterns.route(conversation_analysis_url)
def index(request, conversation, slug):
    mongodb_wrapper = MongodbWrapper(conversation.id)
    if mongodb_wrapper.conversation_data_exists():
        utm_source_options = mongodb_wrapper.get_utm_sources()
        utm_campaign_options = mongodb_wrapper.get_utm_campaigns()
        utm_medium_options = mongodb_wrapper.get_utm_medium()
        return {
            "conversation": conversation,
            "utm_source_options": utm_source_options,
            "utm_campaign_options": utm_campaign_options,
            "utm_medium_options": utm_medium_options,
            "data_exists": True,
        }
    return {"data_exists": False, "conversation": conversation}


@urlpatterns.route(conversation_analysis_url_aquisition_viz)
def aquisition(request, conversation, slug):
    start_date = datetime.date.fromisoformat(request.GET.get("startDate"))
    end_date = datetime.date.fromisoformat(request.GET.get("endDate"))
    view_id = request.GET.get("viewId")
    utm_medium = request.GET.get("utmMedium")
    utm_campaign = request.GET.get("utmCampaign")
    utm_source = request.GET.get("utmSource")
    analytics_wrapper = AnalyticsWrapper(
        start_date, end_date, view_id, utm_medium, utm_campaign, utm_source
    )
    engajement = analytics_wrapper.get_page_engajement()
    mongodb_wrapper = MongodbWrapper(
        conversation.id, start_date, end_date, utm_medium, utm_campaign, utm_source
    )
    aquisition = mongodb_wrapper.get_page_aquisition()
    d3js_wrapper = D3jsWrapper(aquisition, engajement)
    return JsonResponse(d3js_wrapper.get_aquisition_viz_data())


@urlpatterns.route(conversation_analysis_url_aquisition_viz_start_collect)
def trigger_collect(request, conversation, slug):
    airflow_client = AirflowClient(conversation.id)
    airflow_client.trigger_dag()
    return JsonResponse({})
