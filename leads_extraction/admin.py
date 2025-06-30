from django.contrib import admin
from .models import Funnel, Stage, Lead

# Register your models here.
admin.site.register(Funnel)
admin.site.register(Stage)
admin.site.register(Lead)