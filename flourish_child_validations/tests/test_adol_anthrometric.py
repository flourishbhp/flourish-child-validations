from django.test import TestCase, tag
from django.utils import timezone
from django.core.exceptions import ValidationError
from ..form_validators import AnthropometricFormValidator
from .models import ChildVisit, Appointment
from .test_model_mixin import TestModeMixin


@tag('at')
class TestAnthropometricFormValidator(TestModeMixin, TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(AnthropometricFormValidator, *args, **kwargs)

    def setUp(self):
        appointment = Appointment.objects.create(
            subject_identifier='2334432',
            appt_datetime=timezone.now(),
            visit_code='2000',
            visit_instance='0')

        child_visit = ChildVisit.objects.create(
            subject_identifier='12345323',
            appointment=appointment)
        
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
        