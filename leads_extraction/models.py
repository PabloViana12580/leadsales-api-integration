"""
Leadsales API Models

Models to be stored in database after API call to leadsales

Guatemala 28 de Junio 2024
Cliente: Logicomer
Dev: PV pabloviana
---------
"""

import datetime 


from django.db import models
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField

class Funnel(models.Model):

	funnelid = models.CharField(max_length = 1000, primary_key = True)
	funnel_name = models.CharField(max_length = 1000)
	leads_count = models.IntegerField()

class Stage(models.Model):

	funnel = models.ForeignKey(Funnel, on_delete=models.CASCADE, related_name='stages')
	stageid = models.CharField(max_length = 1000, primary_key = True)
	stagename = models.CharField(max_length = 1000)
	leads_count = models.IntegerField()
	expires_after = models.IntegerField()
	order = models.IntegerField()
	sum_value = models.FloatField()

class Lead(models.Model):

	stage = models.ForeignKey(Stage, on_delete=models.CASCADE, related_name='lead')
	leadid = models.CharField(max_length = 1000, primary_key = True)
	value = models.IntegerField()
	company = "logicomer"
	funnel = models.TextField()
	phonenumber = PhoneNumberField(region=None)
	status = models.TextField()
	email = models.EmailField()
	name = models.TextField()
	user_assgnee = models.TextField()

	#String method of the class
	def __str__(self):
		return self.phonenumber