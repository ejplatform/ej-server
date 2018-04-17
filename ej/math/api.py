import ej.math.api_views


def register(router):
    router.register(r'jobs', ej.math.api_views.JobViewSet, base_name='job')