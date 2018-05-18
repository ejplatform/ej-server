from django.contrib.auth import get_user_model

from ej.ej_jobs import task
from ej.ej_jobs.models import JsonTask

User = get_user_model()


@task(JsonTask)
def simple_task(obj):
    return {
        'id': obj.id,
        'data': str(obj),
    }


class TestJsonTask:
    def test_json_task_handler(self, db):
        user = User.objects.create(username='foo')
        expect = simple_task(user)

        assert JsonTask.objects.count() == 0
        assert simple_task.call(user) == expect
        assert JsonTask.objects.count() == 1
