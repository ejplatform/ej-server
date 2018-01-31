from rest_framework.routers import SimpleRouter

from . import views

router = SimpleRouter()
router.register(r'', views.JobViewSet)
router.register(
    r'',
    views.JobViewSet,
    base_name='conversation-job'
)

urlpatterns = router.urls
