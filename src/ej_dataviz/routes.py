from boogie.router import Router
from ej_dataviz.tables import test

urlpatterns = Router(
    template='ej_dataviz/{name}.jinja2',
)


@urlpatterns.route('', login=False)
def index():
    table = test()
    return {
        'table': table,
    }
