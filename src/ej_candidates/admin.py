from django.contrib import admin

from .models.candidate import Candidate
from .models.selected_candidates import SelectedCandidate
from .models.pressed_candidates import PressedCandidate
from .models.ignored_candidates import IgnoredCandidate

admin.site.register(Candidate)
admin.site.register(SelectedCandidate)
admin.site.register(PressedCandidate)
admin.site.register(IgnoredCandidate)
