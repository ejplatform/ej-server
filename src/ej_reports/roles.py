from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from hyperpython import div, button, p, a
from hyperpython.django import csrf_input
from boogie import rules


#
# Button role
#
def file_button(information):
    """
    Render a button on reports page.
    """
    content = []
    for item, files in information.items():
        key_name = item
        for name, type in files.items():
            content.append(p(a(name, href_=f'{item}.{type}')))

    return div(class_='dropdown') [
        button(f'Download {key_name} data', class_='dropbtn'),
        div(class_='dropdown-content')[content]
    ]
