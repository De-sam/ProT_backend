# tailoring/admin.py
from django.contrib import admin
from .models import MeasurementCategory, Measurement, Design

admin.site.register(MeasurementCategory)
admin.site.register(Measurement)
admin.site.register(Design)
