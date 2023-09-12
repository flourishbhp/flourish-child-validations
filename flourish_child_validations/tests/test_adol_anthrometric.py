from django.test import TestCase, tag
from django.core.exceptions import ValidationError
from edc_base.utils import get_utcnow

from ..form_validators import AnthropometricFormValidator
from .models import (ChildVisit, Appointment, ActionItem, ActionType,
                     RegisteredSubject)
from .test_model_mixin import TestModelMixin


@tag('at')
class TestAnthropometricFormValidator(TestModelMixin, TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(AnthropometricFormValidator, *args, **kwargs)

    def setUp(self):
        appointment = Appointment.objects.create(
            subject_identifier='2334432-1',
            appt_datetime=get_utcnow(),
            visit_code='2000',
            visit_instance='0')

        child_visit = ChildVisit.objects.create(
            appointment=appointment)

        action_type = ActionType.objects.create(
            name='submit-childoff-study')

        ActionItem.objects.create(
            subject_identifier=appointment.subject_identifier,
            action_type=action_type)

        RegisteredSubject.objects.create(
            subject_identifier=appointment.subject_identifier,
            relative_identifier='2334432')
        
        self.data = {
            'child_visit': child_visit,
            'systolic_bp': 170,
            'diastolic_bp': 100
        }
        
        
    def test_diastolic_less_than_systolic(self):
        
        self.data['diastolic_bp'] = 200
        
        form_validator = AnthropometricFormValidator(cleaned_data=self.data)
        
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('diastolic_bp', form_validator._errors) 
        