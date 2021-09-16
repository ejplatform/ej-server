import datetime
import json

from boogie.router import Router
from django.http import HttpResponse
from django.http import JsonResponse
from django.utils.translation import ugettext_lazy as _
from ej_conversations import models
from .forms import OpinionComponentForm
from .models import OpinionComponent

from .airflow_client import AirflowClient
from .visualizations.opinion_component.lib.analytics_wrapper import AnalyticsWrapper
from .visualizations.opinion_component.lib.d3js_wrapper import D3jsWrapper
from .visualizations.opinion_component.lib.mongodb_wrapper import MongodbWrapper
from django.shortcuts import redirect

app_name = "ej_analysis"
urlpatterns = Router(
    template="ej_analysis/{name}.jinja2",
    models={"conversation": models.Conversation},
    login=True,
)
conversation_analysis_url = f"<model:conversation>/<slug:slug>/analysis"
conversation_analysis_url_aquisition_viz = f"<model:conversation>/<slug:slug>/analysis/opinion_component"
conversation_analysis_url_start_opinion_component_analysis = (
    f"<model:conversation>/<slug:slug>/analysis/start_opinion_component_analysis"
)


@urlpatterns.route(conversation_analysis_url)
def index(request, conversation, slug):
    mongodb_wrapper = MongodbWrapper(conversation.id)
    try:
        mongodb_wrapper.try_mongodb_connection()
    except:
        return mongodb_timeout_state(conversation)
    try:
        opinion_component = OpinionComponent.objects.get(conversation_id=conversation.id)
        airflow_client = AirflowClient(conversation.id, opinion_component.analytics_property_id)
        if airflow_client.lattest_dag_is_running():
            return collecting_data_state(conversation)
        if mongodb_wrapper.conversation_data_exists():
            return data_collected_state(conversation, mongodb_wrapper)
        return missing_data_state(conversation)
    except:
        return missing_data_state(conversation)


def mongodb_timeout_state(conversation):
    return {
        "mongodb_timeout": True,
        "data_exists": False,
        "conversation": conversation,
        "collecting_is_running": False,
    }


def collecting_data_state(conversation):
    return {
        "conversation": conversation,
        "data_exists": False,
        "mongodb_timeout": False,
        "collecting_is_running": True,
    }


def data_collected_state(conversation, mongodb_wrapper):
    return {
        "conversation": conversation,
        "utm_source_options": mongodb_wrapper.get_utm_sources(),
        "utm_campaign_options": mongodb_wrapper.get_utm_campaigns(),
        "utm_medium_options": mongodb_wrapper.get_utm_medium(),
        "data_exists": True,
        "mongodb_timeout": False,
        "collecting_is_running": False,
    }


def missing_data_state(conversation):
    return {
        "conversation": conversation,
        "utm_source_options": [],
        "utm_campaign_options": [],
        "utm_medium_options": [],
        "data_exists": False,
        "mongodb_timeout": False,
        "collecting_is_running": False,
    }


@urlpatterns.route(conversation_analysis_url_aquisition_viz)
def opinion_component(request, conversation, slug):
    start_date = datetime.date.fromisoformat(request.GET.get("startDate"))
    end_date = datetime.date.fromisoformat(request.GET.get("endDate"))
    utm_medium = request.GET.get("utmMedium")
    utm_campaign = request.GET.get("utmCampaign")
    utm_source = request.GET.get("utmSource")
    try:
        opinion_component = OpinionComponent.objects.get(conversation_id=conversation.id)
        analytics_wrapper = AnalyticsWrapper(
            start_date,
            end_date,
            opinion_component.analytics_property_id,
            utm_medium,
            utm_campaign,
            utm_source,
        )
        engajement = analytics_wrapper.get_page_engajement()
        mongodb_wrapper = MongodbWrapper(
            conversation.id, start_date, end_date, utm_medium, utm_campaign, utm_source
        )
        aquisition = mongodb_wrapper.get_page_aquisition()
        d3js_wrapper = D3jsWrapper(aquisition, engajement)
        return JsonResponse(d3js_wrapper.get_aquisition_viz_data())
    except Exception as e:
        print("Could not generate D3js data")
        print(e)
        return JsonResponse({})


@urlpatterns.route(conversation_analysis_url_start_opinion_component_analysis)
def start_opinion_component_analysis(request, conversation, slug):
    if request.method == "POST":
        form = OpinionComponentForm(request.POST)
        if form.is_valid():
            try:
                opinion_component = OpinionComponent.objects.get(
                    analytics_property_id=request.POST.get("analytics_property_id")
                )
            except:
                opinion_component = form.save()
            airflow_client = AirflowClient(conversation.id, opinion_component.analytics_property_id)
            airflow_client.trigger_dag()
    return redirect("conversation-analysis:index", conversation=conversation, slug=slug)
