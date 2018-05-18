from rest_framework.routers import DefaultRouter

import ej_conversations.api
from .utils import register_module as register

# Define all internal urls
router_v1 = DefaultRouter()
register(router_v1, 'ej.users.api')
# register(router_v1, 'ej.math.api')
register(router_v1, 'ej.gamification.api')

ej_conversations.api.register_routes(router_v1, register_user=True)
