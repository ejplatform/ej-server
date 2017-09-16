from django.conf.urls import url
from django.views.generic import TemplateView


urlpatterns = [
    url(r'^embed.js',
        TemplateView.as_view(template_name='polis/embed.js', content_type='text/javascript'),
        name='polis-embed'),
]
