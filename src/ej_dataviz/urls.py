from django.urls import path
from . import views_dataviz
from . import views_report

app_name = "ej_dataviz"
conversation_url = f"<int:conversation_id>/<slug:slug>/"
report_url = f"<int:conversation_id>/<slug:slug>/report/"

urlpatterns = [
    path(
        conversation_url + "dashboard/",
        views_dataviz.index,
        name="index",
    ),
    path(
        conversation_url + "communication/",
        views_dataviz.communication,
        name="communication",
    ),
    path(
        conversation_url + "scatter/",
        views_dataviz.scatter,
        name="scatter",
    ),
    path(
        conversation_url + "scatter/pca.json/",
        views_dataviz.scatter_pca_json,
        name="scatter_pca_json",
    ),
    path(
        conversation_url + "scatter/group-<groupby>.json",
        views_dataviz.scatter_group,
        name="scatter_group",
    ),
    path(
        conversation_url + "dashboard/words.json",
        views_dataviz.words,
        name="words",
    ),
    # reports URLs
    #
    path(
        report_url + "comments-report/",
        views_report.comments_report,
        name="comments_report",
    ),
    path(
        report_url + "comments-report/comments-pagination/",
        views_report.comments_report_pagination,
        name="comments_report_pagination",
    ),
    path(
        report_url + "votes-over-time/",
        views_report.votes_over_time,
        name="votes_over_time",
    ),
    path(
        report_url + "users/",
        views_report.users,
        name="users",
    ),
    path(
        report_url + "data/votes.<fmt>",
        views_report.votes_data,
        name="votes_data",
    ),
    path(
        report_url + "data/cluster-<int:cluster_id>/votes.<fmt>",
        views_report.votes_data_cluster,
        name="votes_data_cluster",
    ),
    path(
        report_url + "data/users.<fmt>",
        views_report.users_data,
        name="users_data",
    ),
]
