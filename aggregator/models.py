from django.db import models
from django.contrib.auth import models as auth_models
from datetime import datetime
from django.contrib.auth.models import User

# Create your models here.

class AggregationUnit(models.Model):
    alias = models.CharField(max_length=100)
    mms_name = models.CharField(max_length=100, unique=True)
    w_code = models.CharField(max_length=16, unique=True)

    def __str__(self):
        return self.alias

class Station(models.Model):
    alias = models.CharField(max_length=100)
    mms_name = models.CharField(max_length=100, unique=True)
    w_code = models.CharField(max_length=16, unique=True)
    aggregation_unit = models.ForeignKey(AggregationUnit, on_delete=models.PROTECT)
    p_min = models.IntegerField()
    p_max = models.IntegerField()
    company = models.ForeignKey('Company', on_delete=models.PROTECT, related_name='stations')

    def __str__(self):
        return self.alias

class Schedule(models.Model):
    station = models.ForeignKey(Station, on_delete=models.PROTECT)
    date = models.DateField()
    version = models.PositiveIntegerField(default=1)  # version of the schedule
    schedule =  models.JSONField() # JSON field to store 24-hour schedule (23, 25 hours)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('auth.User', on_delete=models.PROTECT)
    # TODO: date + version + station is unique
    def __str__(self):
        return f"Schedule for {self.station.alias} for {self.date} (v{self.version})"
    

class Company(models.Model):
    name = models.CharField(max_length=100)
    mms_name = models.CharField(max_length=100, unique=True)
    x_code = models.CharField(max_length=16, unique=True)
    users = models.ManyToManyField(User, blank=True)

    def __str__(self):
        return self.name
    

def get_version(station: Station, date: datetime) -> int:
    """
    Returns the version of the schedule for the given station and date.
    If no schedule exists, returns 1.
    """
    # order by version descending
    schedule = Schedule.objects.filter(station=station, date=date).order_by('-version').first()
    if schedule:
        return schedule.version + 1
    return 1

# TODO: PRS -> date, CDT, create_by, version, json

class CommerceReport(models.Model):
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('auth.User', on_delete=models.PROTECT)
    created_by = models.ForeignKey('auth.User', on_delete=models.PROTECT)
    version = models.PositiveIntegerField(default=1)
    report = models.JSONField()

    def __str__(self):
        return f"Commerce Report for {self.date} (v{self.version})"
    

def get_commerce_version(date: datetime) -> int:
    """
    Returns the version of the commerce report for the given date.
    If no report exists, returns 1.
    """
    # order by version descending
    report = CommerceReport.objects.filter(date=date).order_by('-version').first()
    if report:
        return report.version + 1
    return 1

    # Here we are extending user model
def is_dispatcher(self):
    return self.is_staff


auth_models.User.add_to_class('is_dispatcher', property(is_dispatcher))


def is_generation(self):
    return not self.is_staff


auth_models.User.add_to_class('is_generation', property(is_generation))
    