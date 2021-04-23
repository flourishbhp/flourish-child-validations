from django_crypto_fields.fields import IdentityField
from django.db import models
from django.db.models.deletion import PROTECT
from edc_base.model_mixins import BaseUuidModel
from edc_base.utils import get_utcnow


class Appointment(BaseUuidModel):

    subject_identifier = models.CharField(max_length=25)

    appt_datetime = models.DateTimeField(default=get_utcnow)

    visit_code = models.CharField(max_length=25)

    visit_instance = models.CharField(max_length=25)


class CaregiverConsent(BaseUuidModel):

    subject_identifier = models.CharField(max_length=25)

    screening_identifier = models.CharField(max_length=50)

    consent_datetime = models.DateTimeField()

    dob = models.DateField()

    version = models.CharField(
        max_length=10,
        editable=False)

    child_dob = models.DateField(blank=True, null=True)


class CaregiverChildConsent(BaseUuidModel):

    subject_identifier = models.CharField(max_length=25)

    screening_identifier = models.CharField(max_length=50)

    consent_datetime = models.DateTimeField()

    child_dob = models.DateField()

    gender = models.CharField(max_length=10)

    identity = IdentityField(
        verbose_name='Identity number')

    version = models.CharField(
        max_length=10,
        editable=False)


class ChildAssent(BaseUuidModel):

    subject_identifier = models.CharField(max_length=25)

    screening_identifier = models.CharField(max_length=50)

    consent_datetime = models.DateTimeField()

    dob = models.DateField()

    identity = IdentityField(
        verbose_name='Identity number')

    version = models.CharField(
        max_length=10,
        editable=False)


class ChildDataset(BaseUuidModel):

    study_child_identifier = models.CharField(max_length=36)

    infant_sex = models.CharField(max_length=7)


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


class ScreeningPriorBhpParticipants(BaseUuidModel):

    screening_identifier = models.CharField(max_length=50)

    report_datetime = models.DateTimeField()

    study_child_identifier = models.CharField(max_length=50)
