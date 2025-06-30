from django.shortcuts import render
from django.http import HttpResponse
from .models import Funnel
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