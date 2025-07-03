from django.urls import path
from .views import funnels_view, stages_view, single_funnel_stages

from . import views

app_name = "leads"
urlpatterns = [
    path("", views.index, name="index"),
    path("funnels/", funnels_view, name='funnels'),
    path("stages/", stages_view, name='stages'),
    path('stages/<str:funnelid>/', single_funnel_stages, name='funnel_stages')
]