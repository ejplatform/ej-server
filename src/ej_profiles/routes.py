from django.shortcuts import render, redirect

from boogie.router import Router
from .forms import ProfileForm

urlpatterns = Router()


@urlpatterns.route('', login=True)
def detail(request):
    ctx = dict(info_tab=request.GET.get('info', 'profile'))
    return render(request, 'ej_profiles/profile-detail.jinja2', ctx)


@urlpatterns.route('edit/', login=True)
def edit(request):
    profile = request.user
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile, files=request.FILES)
        if form.is_valid():
            form.save()
            return redirect('/profile/')
    else:
        form = ProfileForm(instance=request.user)

    ctx = dict(form=form, profile=profile)
    return render(request, 'ej_profiles/profile-edit.jinja2', ctx)
