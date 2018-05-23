from django.shortcuts import render, redirect
from boogie.router import Router
from ej_dataviz.tables import *
urlpatterns = Router()


@urlpatterns.route('', login=False)
def index(request):
    table = render_dataframe(None)
    ctx = dict(table=table)
    return render(request, 'ej_dataviz/index.jinja2', ctx)

