from django.utils.translation import ugettext_lazy as _
from hyperpython import a

from ej.components.menu import register_menu


#
# Register menu links
#
@register_menu("conversations:detail-actions")
def dataviz_links(request, conversation):
    return [
        a(_("Scatter plot"), href=conversation.url("dataviz:scatter")),
        a(_("Word cloud"), href=conversation.url("dataviz:word-cloud")),
    ]


@register_menu("conversations:detail-admin")
def report_links(request, conversation):
    if request.user.has_perm("ej.can_view_report", conversation):
        return [a(_("Usage report"), href=conversation.url("report:index"))]
    else:
        return []
