from rest_framework.routers import SimpleRouter

from . import views

router = SimpleRouter()

router.register(
    r'jobs',
    views.JobViewSet,
    base_name='job'
)

urlpatterns = router.urls
