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
    for type, filename in information.items():
        content.append(p(a(type, href_=filename)))

    return div(class_='dropdown') [
        button('Download users data', class_='dropbtn'),
        div(class_='dropdown-content')[content]
    ]
