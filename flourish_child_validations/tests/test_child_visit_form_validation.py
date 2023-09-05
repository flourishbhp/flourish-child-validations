from dateutil.relativedelta import relativedelta
from django.core.exceptions import ValidationError
from django.test import TestCase
from edc_base.utils import get_utcnow
from edc_constants.constants import FEMALE

from ..form_validators import ChildVisitFormValidator
from .models import CaregiverChildConsent, RegisteredSubject
from .models import CaregiverConsent, Appointment, ScreeningPriorBhpParticipants
from .test_model_mixin import TestModelMixin


class VisitSequence:
    def __init__(self, appointment=None):
        self.appointment = appointment
        self.previous_visit_missing = False

    def enforce_sequence(self):
        pass


class TestChildVisitFormValidator(TestModelMixin, TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(ChildVisitFormValidator, *args, **kwargs)

    def setUp(self):
        ChildVisitFormValidator.visit_sequence_cls = VisitSequence
        ScreeningPriorBhpParticipants.objects.create(
            screening_identifier='S99112',
            report_datetime=get_utcnow())

        self.subject_consent = CaregiverConsent.objects.create(
            subject_identifier='1234567-10',
            screening_identifier='S99112',
            consent_datetime=get_utcnow() - relativedelta(years=2),
            dob=get_utcnow() - relativedelta(years=25),
            version='1')

        self.caregiver_child_consent = CaregiverChildConsent.objects.create(
            subject_identifier=self.subject_consent.subject_identifier,
            consent_datetime=get_utcnow() - relativedelta(years=2),
            child_dob=(get_utcnow() - relativedelta(years=5)).date(),
            gender=FEMALE,
            identity='123425678',
            version='1',)

        self.appointment = Appointment.objects.create(
            subject_identifier=self.subject_consent.subject_identifier,
            appt_datetime=get_utcnow(),
            visit_code='2000')

        RegisteredSubject.objects.create(
            subject_identifier=self.subject_consent.subject_identifier,
            relative_identifier='1234567', )

    def test_current_consent_version_exists(self):
        cleaned_data = {
            'appointment': self.appointment,
            'subject_identifier': self.subject_consent.subject_identifier}
        form_validator = ChildVisitFormValidator(cleaned_data=cleaned_data)
        try:
            form_validator.validate()
        except ValidationError as e:
            self.fail(f'ValidationError unexpectedly raised. Got{e}')
