from django.contrib import admin

from .models.candidate import Candidate
from .models.selected_candidates import SelectedCandidate

admin.site.register(Candidate)
admin.site.register(SelectedCandidate)
