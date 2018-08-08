from django.contrib import admin

from .models.candidate import Candidate
from .models.selected_candidates import SelectedCandidate
from .models.pressed_candidates import PressedCandidate

admin.site.register(Candidate)
admin.site.register(SelectedCandidate)
admin.site.register(PressedCandidate)
