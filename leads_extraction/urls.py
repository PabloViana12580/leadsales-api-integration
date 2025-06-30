from django.urls import path
from .views import funnels_view

from . import views

app_name = "leads"
urlpatterns = [
    path("", views.index, name="index"),
    path("funnels/", funnels_view, name='funnels')
]