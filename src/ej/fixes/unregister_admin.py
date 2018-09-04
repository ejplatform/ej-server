#
# Unregister certain apps from the production admin
#
from django.apps import apps
from django.contrib import admin

UNREGISTER_APPS = [
    'authtoken',
]


def unregister_app(app_label):
    app = apps.get_app_config(app_label)
    for model in app.get_models():
        if admin.site.is_registered(model):
            admin.site.unregister(model)


def unregister_apps():
    for app in UNREGISTER_APPS:
        unregister_app(app)
