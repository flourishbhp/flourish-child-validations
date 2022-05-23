from django.test import TestCase, tag
from django.core.exceptions import ValidationError
from flourish_child_validations.form_validators import ChildPregTestingFormValidator
from .models import ChildVisit, Appointment
from django.utils import timezone
from edc_base.utils import get_utcnow
from dateutil.relativedelta import relativedelta
from edc_constants.constants import NO, YES, NOT_APPLICABLE,FEMALE,MALE


class TestChildPregnacyFormValidator(TestCase):
    
    def setUp(self):
        flourish_consent_version_model = 'flourish_child_validations.flourishconsentversion'
        subject_consent_model = 'flourish_child_validations.subjectconsent'
        child_caregiver_consent_model = 'flourish_child_validations.caregiverchildconsent'
        
        ChildPregTestingFormValidator.consent_version_model = flourish_consent_version_model
        ChildPregTestingFormValidator.subject_consent_model = subject_consent_model
        ChildPregTestingFormValidator.child_caregiver_consent_model = child_caregiver_consent_model

        appointment = Appointment.objects.create(
            subject_identifier='2334432',
            appt_datetime=timezone.now(),
            visit_code='2001',
            visit_instance='0',
           )

        child_visit = ChildVisit.objects.create(
            subject_identifier='12345323',
            appointment=appointment,
            schedule_name='child_a_quart_schedule1',)
        
        self.options = {
            'test_done': YES,
            'last_menstrual_period': get_utcnow(),
            'is_lmp_date_estimated': NO,
            'preg_test_result': 'Negative',   
            'child_visit': child_visit,  
            }

    def test_pregnacy_test_valid(self):
            
            field_name = 'test_done'
            self.options[field_name] = YES
            self.options['last_menstrual_period'] = (get_utcnow() - relativedelta(months=2)).date()
            
            form_validator = ChildPregTestingFormValidator(cleaned_data=self.options)
            try:
                form_validator.validate()
            except ValidationError as e:
                self.fail(f'ValidationError unexpectedly raised. Got{e}')
            
    def test_pregnancy_test_results_required(self):

        field_name = 'preg_test_result'
        self.options[field_name] = None
        
        form_validator = ChildPregTestingFormValidator(cleaned_data=self.options)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn(field_name, form_validator._errors)
        
    def test_pregnancy_test_results_valid(self):

        field_name = 'preg_test_result'
        self.options[field_name] = 'Positive'
        
        form_validator = ChildPregTestingFormValidator(cleaned_data=self.options)
        try:
            form_validator.validate()
        except ValidationError as e:
            self.fail(f'ValidationError unexpectedly raised. Got{e}')
     

    def test_lmp_date_estimated_required(self):

        field_name = 'is_lmp_date_estimated'
        self.options[field_name] = None

        form_validator = ChildPregTestingFormValidator(cleaned_data=self.options)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn(field_name, form_validator._errors) 
        

    def test_lmp_date_estimated_invalid(self):

        field_name = 'is_lmp_date_estimated'
        self.options.update({'last_menstrual_period': None})

        form_validator = ChildPregTestingFormValidator(cleaned_data=self.options)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn(field_name, form_validator._errors) 
        
        
    def test_lmp_dt_against_today_dt_valid(self):
        
        self.options['last_menstrual_period'] = (get_utcnow() - relativedelta(months=2)).date()
        
        form_validator = ChildPregTestingFormValidator(cleaned_data=self.options)
        try:
            form_validator.validate()
        except ValidationError as e:
            self.fail(f'ValidationError unexpectedly raised. Got{e}')
     
