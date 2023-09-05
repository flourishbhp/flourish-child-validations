from django.core.exceptions import ValidationError
from django.test import TestCase, tag
from edc_base.utils import get_utcnow
from edc_constants.constants import OTHER

from ..form_validators import ChildReferralFUFormValidator
from .models import Appointment, ChildVisit, ListModel, RegisteredSubject
from .test_model_mixin import TestModelMixin

class TestChildRefferalFormValidator(TestModelMixin, TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(ChildReferralFUFormValidator, *args, **kwargs)

    def setUp(self):
        appointment = Appointment.objects.create(
            subject_identifier='2334432-1',
            appt_datetime=get_utcnow(),
            visit_code='2000',
            visit_instance='0')

        self.child_visit = ChildVisit.objects.create(
            subject_identifier='12345323',
            appointment=appointment)

        RegisteredSubject.objects.create(
            subject_identifier=appointment.subject_identifier,
            relative_identifier='2334432', )

        ListModel.objects.create(name=OTHER, short_name=OTHER)

    @tag('emo')
    def test_emo_support_type_other(self):
        """
               Raise an error if the emo support type other is not captured.
               """

        cleaned_data = {
            'child_visit': self.child_visit,
            'emo_support_type': ListModel.objects.all(),
            'emo_support_type_other': None
        }

        form_validator = ChildReferralFUFormValidator(
            cleaned_data=cleaned_data)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('emo_support_type_other', form_validator._errors)
