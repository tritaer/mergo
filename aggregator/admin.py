from django.contrib import admin
from .models import AggregationUnit, Station, Schedule, Company

# Register your models here.
admin.site.register(AggregationUnit)
admin.site.register(Station)
admin.site.register(Schedule)
admin.site.register(Company)
