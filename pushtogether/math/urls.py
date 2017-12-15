from rest_framework.routers import SimpleRouter

from .views import JobViewSet

router = SimpleRouter()
router.register(r'jobs', JobViewSet)
