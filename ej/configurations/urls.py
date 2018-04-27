from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='configurations-index'),
    path('styles/', views.styles, name='configurations-styles'),
    path('info/', views.info, name='configurations-info'),
    path('fragments/', views.fragment_list, name='configurations-fragments'),
    path('fragments/<name>/', views.fragment_error, name='configurations-fragment-error'),
]
