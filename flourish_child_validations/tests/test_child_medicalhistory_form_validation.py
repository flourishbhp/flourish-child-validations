from django.test import TestCase,tag
from django.core.exceptions import ValidationError
from edc_constants.constants import NO, YES
from flourish_child_validations.form_validators import ChildMedicalHistoryFormValidator
from .models import ChildVisit, Appointment
from django.utils import timezone
from edc_base.utils import get_utcnow

@tag('lmp2')
class TestChildMedicalHistoryFormValidator(TestCase):
    
    def setUp(self):
        
        flourish_consent_version_model = 'flourish_child_validations.flourishconsentversion'
        ChildMedicalHistoryFormValidator.consent_version_model = flourish_consent_version_model
        subject_consent_model = 'flourish_child_validations.subjectconsent'
        ChildMedicalHistoryFormValidator.subject_consent_model = subject_consent_model
        
        appointment = Appointment.objects.create(
            subject_identifier='2334432',
            appt_datetime=timezone.now(),
            visit_code='2000',
            visit_instance='0')

        child_visit = ChildVisit.objects.create(
            subject_identifier='12345323',
            appointment=appointment)

        self.data = {
            'preg_test_performed': YES,
            'last_menstrual_period': get_utcnow(),
            'is_lmp_date_estimated': NO,
            'pregnancy_test_result': 'Negative',   
            'child_visit': child_visit,  
        }
        
     
    def test_pregnancy_test_results_required(self):
        
        field_name = 'pregnancy_test_result'
        self.data[field_name] = None
        
        form_validator = ChildMedicalHistoryFormValidator(cleaned_data=self.data)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn(field_name, form_validator._errors)
        
    def test_lmp_date_estimated_required(self):
        
        field_name = 'is_lmp_date_estimated'
        self.data[field_name] = None
        
        form_validator = ChildMedicalHistoryFormValidator(cleaned_data=self.data)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn(field_name, form_validator._errors)
        
    def test_lmp_required(self):
        
        field_name = 'last_menstrual_period'
        self.data[field_name] = None
        
        form_validator = ChildMedicalHistoryFormValidator(cleaned_data=self.data)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn(field_name, form_validator._errors) 
        
        
    def test_lmp_dt_against_today_dt(self):
        
        field_name = 'last_menstrual_period'
        self.data[field_name] = get_utcnow().date()
        
        form_validator = ChildMedicalHistoryFormValidator(cleaned_data=self.data)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn(field_name, form_validator._errors) 
     
        
        
     
     
