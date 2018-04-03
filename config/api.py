from rest_framework.routers import DefaultRouter

from .utils import register_module as register

# Define all application urls
router_v1 = DefaultRouter()
register(router_v1, 'ej.users.api')
