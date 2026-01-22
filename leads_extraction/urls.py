from django.urls import path
from .views import funnels_view, stages_view, single_funnel_stages, leads_view, export_leads_csv

from . import views

app_name = "leads"
urlpatterns = [
    path("", funnels_view, name="index"),
    path("funnels/", funnels_view, name='funnels'),
    path("stages/", stages_view, name='stages'),
    path('stages/<str:funnelid>/', single_funnel_stages, name='funnel_stages'),
    path("leads/<str:stageid>/", leads_view, name='leads_for_stage'),
    path("export/csv/<str:stage_id>/", export_leads_csv, name="export_leads_csv")
]