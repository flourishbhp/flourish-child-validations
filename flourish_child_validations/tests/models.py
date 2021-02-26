from django.db import models
from django.db.models.deletion import PROTECT
from edc_base.model_mixins import BaseUuidModel
from edc_base.utils import get_utcnow


class Appointment(BaseUuidModel):

    subject_identifier = models.CharField(max_length=25)

    appt_datetime = models.DateTimeField(default=get_utcnow)

    visit_code = models.CharField(max_length=25)

    visit_instance = models.CharField(max_length=25)


class ChildVisit(BaseUuidModel):

    subject_identifier = models.CharField(max_length=25)

    appointment = models.OneToOneField(Appointment, on_delete=PROTECT)

    report_datetime = models.DateTimeField(default=get_utcnow)


class RegisteredSubject(BaseUuidModel):

    subject_identifier = models.CharField(
        max_length=50,
        unique=True)

    relative_identifier = models.CharField(
        max_length=36,
        null=True,
        blank=True)
