from django.db import models
from django.db.models.deletion import PROTECT
from django.utils import timezone
from django_crypto_fields.fields import IdentityField
from edc_base.model_mixins import BaseUuidModel, ListModelMixin
from edc_base.utils import get_utcnow
from edc_constants.constants import NEW


class ListModel(ListModelMixin, BaseUuidModel):
    pass


class ActionType(BaseUuidModel):
    name = models.CharField(max_length=50, )


class ActionItem(BaseUuidModel):
    subject_identifier = models.CharField(max_length=25)

    action_identifier = models.CharField(max_length=25)

    report_datetime = models.DateTimeField(
        default=get_utcnow)

    action_type = models.ForeignKey(
        ActionType, on_delete=PROTECT, )

    status = models.CharField(max_length=25, default=NEW, )

    def action_cls(self, reference_model_obj=None):
        pass


class Appointment(BaseUuidModel):
    subject_identifier = models.CharField(max_length=25)

    appt_datetime = models.DateTimeField(default=get_utcnow)

    visit_code = models.CharField(max_length=25)

    visit_code_sequence = models.IntegerField(default=0)

    visit_instance = models.CharField(max_length=25)

    visit_schedule_name = models.CharField(max_length=25)

    @classmethod
    def related_visit_model_attr(cls):
        return 'childvisit'


class CaregiverConsent(BaseUuidModel):
    subject_identifier = models.CharField(max_length=25)

    screening_identifier = models.CharField(max_length=50)

    consent_datetime = models.DateTimeField()

    dob = models.DateField()

    version = models.CharField(
        max_length=10,
        editable=False)

    child_dob = models.DateField(blank=True, null=True)


class SubjectConsent(BaseUuidModel):
    subject_identifier = models.CharField(max_length=25)

    screening_identifier = models.CharField(max_length=50)

    gender = models.CharField(max_length=25)

    is_literate = models.CharField(max_length=25,
                                   blank=True,
                                   null=True)

    witness_name = models.CharField(max_length=25,
                                    blank=True,
                                    null=True)

    dob = models.DateField()

    consent_datetime = models.DateTimeField()

    version = models.CharField(
        max_length=10,
        editable=False)


class CaregiverChildConsent(BaseUuidModel):
    subject_identifier = models.CharField(max_length=25)

    screening_identifier = models.CharField(max_length=50)

    consent_datetime = models.DateTimeField()

    child_dob = models.DateField()

    gender = models.CharField(max_length=10)

    identity = IdentityField(
        verbose_name='Identity number',
        null=True, blank=True)

    identity_type = models.CharField(
        verbose_name='What type of identity number is this?',
        max_length=25,
        null=True,
        blank=True)

    confirm_identity = IdentityField(
        help_text='Retype the identity number',
        null=True,
        blank=True)

    version = models.CharField(
        max_length=10,
        editable=False)


class ChildAssent(BaseUuidModel):
    subject_identifier = models.CharField(max_length=25)

    screening_identifier = models.CharField(max_length=50)

    consent_datetime = models.DateTimeField()

    dob = models.DateField()

    identity = IdentityField(
        verbose_name='Identity number',
        null=True, blank=True)

    version = models.CharField(
        max_length=10,
        editable=False)


class ChildDataset(BaseUuidModel):
    study_child_identifier = models.CharField(max_length=36)

    infant_sex = models.CharField(max_length=7)


class OnSchedule(BaseUuidModel):
    subject_identifier = models.CharField(
        max_length=50)
    schedule_name = models.CharField(max_length=25, blank=True, null=True)

    child_subject_identifier = models.CharField(
        max_length=50)


class Schedule(BaseUuidModel):
    subject_identifier = models.CharField(
        max_length=50)

    child_subject_identifier = models.CharField(
        max_length=50)

    schedule_name = models.CharField(max_length=25, blank=True, null=True)

    onschedule_model = models.CharField(max_length=25, blank=True, null=True)


class ChildVisit(BaseUuidModel):
    subject_identifier = models.CharField(max_length=25)

    appointment = models.OneToOneField(Appointment, on_delete=PROTECT)

    report_datetime = models.DateTimeField(default=get_utcnow)

    schedule_name = models.CharField(max_length=25)

    visit_code = models.CharField(
        max_length=25, )

    visit_code_sequence = models.CharField(
        max_length=25, )

    @property
    def previous_visit(self):
        previous_visit = None
        previous_appointment = self.appointment.model_cls.objects.filter(
            subject_identifier=self.subject_identifier).order_by(
            '-visit_code_sequence').first()
        if previous_appointment:
            previous_visit = self.model_cls.objects.get(
                appointment=previous_appointment)
        return previous_visit


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


class FlourishConsentVersion(BaseUuidModel):
    screening_identifier = models.CharField(
        max_length=50, )

    version = models.CharField(
        max_length=3)

    report_datetime = models.DateTimeField(
        default=timezone.now, )


class ChildOnScheduleCohortAQuarterly(BaseUuidModel):
    subject_identifier = models.CharField(
        verbose_name="Subject Identifier",
        max_length=50)

    child_subject_identifier = models.CharField(
        verbose_name="Associated Child Identifier",
        max_length=50)


class CaregiverSocioDemographicData(BaseUuidModel):
    maternal_visit = models.OneToOneField(ChildVisit, on_delete=PROTECT)
    stay_with_child = models.CharField(max_length=50)


class InfantFeeding(BaseUuidModel):
    child_visit = models.OneToOneField(ChildVisit, on_delete=PROTECT)


class MaternalDelivery(BaseUuidModel):
    report_datetime = models.DateTimeField()
    subject_identifier = models.CharField(
        max_length=50)


class ChildOffStudy(BaseUuidModel):
    action_name = 'submit-childoff-study'
    subject_identifier = models.CharField(max_length=25)


class ChildBirth(BaseUuidModel):
    subject_identifier = models.CharField(
        max_length=50)

    report_datetime = models.DateTimeField(
        verbose_name="Date and Time infant enrolled", )

    dob = models.DateField()


class ChildPregTesting(BaseUuidModel):
    child_visit = models.OneToOneField(ChildVisit, on_delete=PROTECT)

    menarche = models.CharField(
        max_length=50)


class ChildTannerStaging(BaseUuidModel):
    child_visit = models.OneToOneField(ChildVisit, on_delete=PROTECT)

    manarche_dt_avail = models.CharField(
        max_length=50)

