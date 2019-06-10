from hyperpython import html
import datetime
from django.utils.translation import ugettext as _


@html.register(datetime.datetime, role="simple")
def datetime_simple(obj: datetime.datetime, request=None):
    date = obj.strftime("%x")
    time = obj.strftime("%X")
    return _("{date} at {time}").format(date=date, time=time)
