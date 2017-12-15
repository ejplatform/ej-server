from rest_framework.routers import SimpleRouter

from . import views

router = SimpleRouter()
router.register(r'jobs', views.JobViewSet)

urlpatterns = router.urls
