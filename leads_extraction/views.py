from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, StreamingHttpResponse
from .models import Funnel, Stage, Lead
from .utils import get_funnels, get_leads_for_stage
import csv


class Echo:
    def write(self, value):
        return value


# Create your views here.
def index(request):
    return HttpResponse("Hello, world. You're at the leads extraction index.")
    
def funnels_view(request):
    funnels = get_funnels()

    for funnel_index, funnel in enumerate(funnels):
        
        funnel_name = funnel.get("name", f"Funnel_{funnel_index}")
        stages = funnel.get("stages", [])
        funnel_id = funnel.get("id", f"Funnel_{funnel_index}")

        Funnel.objects.update_or_create(
            funnelid = funnel.get("id", f"Funnel_{funnel_index}"),
            defaults={
                'funnel_name': funnel.get('name', ''),
                'leads_count': funnel.get('leads_count', 0),
            }
        )

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

def single_funnel_stages(request, funnelid):
    funnel = get_object_or_404(Funnel, funnelid=funnelid)
    stages = Stage.objects.filter(funnel=funnel)

    return render(request, "single_funnel_stages.html", {
        "funnel": funnel,
        "stages": stages,
    })

def leads_view(request, stageid):
    leads = get_leads_for_stage(stageid)

    stage_instance = Stage.objects.get(stageid=stageid)

    for lead in leads:
        Lead.objects.update_or_create(
            leadid = lead["id"],
            defaults={
                'stage': stage_instance,
                'value': lead["value"],
                'company': "Logicomer",
                'funnel': lead["funnel"]["id"],
                'phonenumber': lead["handle"],
                'status': lead["status"],
                'email': lead["email"],
                'name': lead["name"],
                'user_assgnee': lead.get('user_assgnee') or "Not Assign"
            }
        )

    return render(request, "leads.html", {"stageid": stageid, "leads": leads})


def export_leads_csv(request, stage_id):
    leads = (
        Lead.objects
        .select_related("stage")
        .filter(stage_id=stage_id)
        .iterator(chunk_size=100)
    )
    total_leads = Lead.objects.filter(stage_id=stage_id).count()

    def stream_csv_rows():
        writer = csv.writer(Echo())
        yield writer.writerow([
            "Stage",
            "Value",
            "Company",
            "Funnel",
            "Phonenumber",
            "Status",
            "Email",
            "Name",
            "Usuario Asignado"
        ])

        for lead in leads:
            yield writer.writerow([
                lead.stage.stagename,
                lead.value,
                lead.company,
                lead.funnel,
                lead.phonenumber,
                lead.status,
                lead.email,
                lead.name,
                lead.user_assgnee
            ])

    response = StreamingHttpResponse(
        stream_csv_rows(),
        content_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="leads.csv"'},
    )
    response["X-Lead-Count"] = total_leads
    response["Cache-Control"] = "no-store"
    return response
