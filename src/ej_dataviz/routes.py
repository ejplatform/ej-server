from boogie.router import Router
from ej_dataviz.plots import test_hist

urlpatterns = Router(
    template='ej_dataviz/{name}.jinja2',
)


@urlpatterns.route('', login=False)
def index():
    # table = test()
    return {
        'table': table,
    }


@urlpatterns.route('histogram', login=False)
def histogram():
    histogram = test_hist()
    return {
        'hist': histogram,
    }
