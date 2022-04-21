from django.test import TestCase, tag
from django.core.exceptions import ValidationError
from edc_constants.constants import NO, YES
from edc_constants.choices import POS_NEG
from flourish_child_validations import form_validators
from flourish_child_validations.form_validators import ChildMedicalHistoryFormValidator

@tag('cmh')
class TestChildMedicalHistoryFormValidator(TestCase):
    
    def setUp(self):
        
        self.data = {
            'is_pregnant': YES,
            'last_menstrual_period': YES,
            'is_lmp_date_estimated': NO,
            'pregnancy_test_result': 'Negative',     
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
        
