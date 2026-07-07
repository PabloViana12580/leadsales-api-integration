from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, StreamingHttpResponse
from .models import Funnel, Stage, Lead
from .utils import get_funnels, get_leads_for_stage
import csv


def save_stage_leads(stage_instance, leads):
    for lead in leads:
        Lead.objects.update_or_create(
            leadid=lead["id"],
            defaults={
                "stage": stage_instance,
                "value": lead.get("value") or 0,
                "company": "Logicomer",
                "funnel": lead.get("funnel", {}).get("id", ""),
                "phonenumber": lead.get("handle", ""),
                "status": lead.get("status", ""),
                "email": lead.get("email", ""),
                "name": lead.get("name", ""),
                "user_assgnee": lead.get("user_assgnee") or "Not Assign",
            },
        )


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
    stage_instance = Stage.objects.get(stageid=stageid)
    leads = get_leads_for_stage(stageid)
    save_stage_leads(stage_instance, leads)

    return render(request, "leads.html", {
        "stageid": stageid,
        "stage": stage_instance,
        "leads": leads,
    })


def export_leads_csv(request, stage_id):
    stage_instance = get_object_or_404(Stage, stageid=stage_id)
    api_leads = get_leads_for_stage(stage_id)
    save_stage_leads(stage_instance, api_leads)
    total_leads = len(api_leads)

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

        for lead in api_leads:
            yield writer.writerow([
                stage_instance.stagename,
                lead.get("value") or 0,
                "Logicomer",
                lead.get("funnel", {}).get("id", ""),
                lead.get("handle", ""),
                lead.get("status", ""),
                lead.get("email", ""),
                lead.get("name", ""),
                lead.get("user_assgnee") or "Not Assign"
            ])

    response = StreamingHttpResponse(
        stream_csv_rows(),
        content_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="leads.csv"'},
    )
    response["X-Lead-Count"] = total_leads
    response["Cache-Control"] = "no-store"
    return response
