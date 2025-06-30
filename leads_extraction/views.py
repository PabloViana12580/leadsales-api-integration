from django.shortcuts import render
from django.http import HttpResponse
from .models import Funnel, Stage, Lead
from .utils import get_funnels

# Create your views here.
def index(request):
    return HttpResponse("Hello, world. You're at the leads extraction index.")
    
def funnels_view(request):
    funnels = get_funnels()

    for funnel_index, funnel in enumerate(funnels):
        
        funnel_name = funnel.get("name", f"Funnel_{funnel_index}")

        Funnel.objects.update_or_create(
            funnelid = funnel.get("id", f"Funnel_{funnel_index}"),
            defaults={
                'funnel_name': funnel.get('name', ''),
                'leads_count': funnel.get('leads_count', 0),
            }
        )

    saved_funnels = Funnel.objects.all()
    return render(request, "funnels.html", {"funnels": saved_funnels})

def stages_view(request):
    funnels = get_funnels()

    for funnel_index, funnel in enumerate(funnels):
        
        stages = funnel.get("stages", [])
        funnel_id = funnel.get("id", f"Funnel_{funnel_index}")

        funnel_instance = Funnel.objects.get(funnelid=funnel_id)

        for stage in stages:
            Stage.objects.update_or_create(
                stageid = stage["id"],
                defaults={
                    'funnel': funnel_instance,
                    'stagename': stage["name"],
                    'leads_count':stage["leads_count"],
                    'expires_after':stage["expires_after"],
                    'order':stage["order"],
                    'sum_value':stage.get('sum_value') or 0.0
                }
            )

    saved_stages = Stage.objects.all()
    return render(request, "stages.html", {"stages": saved_stages})
