from django.test import TestCase, tag
from django.utils import timezone
from django.core.exceptions import ValidationError
from edc_constants.constants import NO, YES
from ..form_validators import TbHistoryFormValidator
from .models import ChildVisit, Appointment
from .test_model_mixin import TestModeMixin


@tag('adol_history')
class TestTbHistoryFormValidator(TestModeMixin, TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(TbHistoryFormValidator, *args, **kwargs)

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
            'prior_tb_infec': NO,
            'history_of_tbt': YES,
            'reason_for_therapy': 'POS',
            'reason_for_therapy_other': None,
            'therapy_prescribed_age': '0_4',
            'tbt_completed': YES,
            'prior_tb_history': YES,
            'tb_diagnosis_type': 'inside_the_lungs',
            'extra_pulmonary_loc': None,
            'other_loc': '',
            'prior_treatmnt_history': YES,
            'tb_drugs_freq': '4_drugs',
            'iv_meds_used': YES,
            'tb_treatmnt_completed': YES}
        
        
    def test_reason_for_therapy_required(self):
        self.data['reason_for_therapy'] = None
        
        form_validator = TbHistoryFormValidator(cleaned_data=self.data)
        
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('reason_for_therapy', form_validator._errors)
        
    def test_therapy_prescribed_age_required(self):
        self.data['therapy_prescribed_age'] = None
        
        form_validator = TbHistoryFormValidator(cleaned_data=self.data)
        
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('therapy_prescribed_age', form_validator._errors)
        
    def test_tbt_completed_required(self):
        self.data['tbt_completed'] = None
        
        form_validator = TbHistoryFormValidator(cleaned_data=self.data)
        
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('tbt_completed', form_validator._errors)
    
    def test_tbt_completed_required(self):
        self.data['tb_drugs_freq'] = None
        
        form_validator = TbHistoryFormValidator(cleaned_data=self.data)
        
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('tb_drugs_freq', form_validator._errors)
        
        
    def test_iv_meds_used_required(self):
        self.data['iv_meds_used'] = None
        
        form_validator = TbHistoryFormValidator(cleaned_data=self.data)
        
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('iv_meds_used', form_validator._errors)
        
    def test_tb_treatmnt_completed_required(self):
        self.data['tb_treatmnt_completed'] = None
        
        form_validator = TbHistoryFormValidator(cleaned_data=self.data)
        
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('tb_treatmnt_completed', form_validator._errors)
        
        
    def test_prior_treatmnt_history_required(self):
        self.data['tbt_completed'] = NO
        
        form_validator = TbHistoryFormValidator(cleaned_data=self.data)
        
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('prior_treatmnt_history', form_validator._errors)
        
