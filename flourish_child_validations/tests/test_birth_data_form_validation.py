from django.core.exceptions import ValidationError
from django.test import TestCase, tag
from django.utils import timezone
from edc_constants.constants import YES, NO

from ..form_validators import BirthDataFormValidator
from .models import ChildVisit, Appointment, Schedule
from .test_model_mixin import TestModeMixin

class TestInfantBirthDataFormValidator(TestModeMixin, TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(BirthDataFormValidator, *args, **kwargs)

    def setUp(self):

        appointment = Appointment.objects.create(
            subject_identifier='2334432',
            appt_datetime=timezone.now(),
            visit_code='2000',
            visit_instance='0')
        
                
        schedule = Schedule.objects.create(
            subject_identifier='2334432-1',

            child_subject_identifier='2334432',

            schedule_name='CohortAQuarterly'
        )
        

        child_visit = ChildVisit.objects.create(
            subject_identifier='12345323',
            appointment=appointment,
            schedule = schedule)


        self.options = {
            'report_datetime': timezone.now(),
            'gestational_age': 25,
            'child_visit': child_visit,
            'weight_kg': 3.61,
            'infant_length': 89.97,
            'head_circumference': 39.30,
            'apgar_score': NO,
            'apgar_score_min_1': None,
            'apgar_score_min_5': 0,
            'apgar_score_min_10': 0,
            'congenital_anomalities': NO,
            'schedule_id': 1,
        }

    def test_validate_apgar_0(self):
        form_validator = BirthDataFormValidator(
            cleaned_data=self.options)
        try:
            form_validator.validate()
        except ValidationError as e:
            self.fail(f'ValidationError unexpectedly raised. Got{e}')

    def test_validate_apgar_1(self):
        self.options['apgar_score'] = YES
        form_validator = BirthDataFormValidator(
            cleaned_data=self.options)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('apgar_score_min_1', form_validator._errors)

    def test_validate_apgar_2(self):
        self.options['apgar_score'] = YES
        self.options['apgar_score_min_1'] = 2
        form_validator = BirthDataFormValidator(
            cleaned_data=self.options)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('apgar_score_min_5', form_validator._errors)

    def test_validate_apgar_3(self):
        self.options['apgar_score'] = YES
        self.options['apgar_score_min_1'] = 2
        self.options['apgar_score_min_5'] = 3
        form_validator = BirthDataFormValidator(
            cleaned_data=self.options)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('apgar_score_min_10', form_validator._errors)

    def test_validate_apgar_4(self):
        self.options['apgar_score'] = NO
        self.options['apgar_score_min_10'] = 3
        form_validator = BirthDataFormValidator(
            cleaned_data=self.options)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('apgar_score_min_10', form_validator._errors)

    def test_validate_apgar_5(self):
        self.options['apgar_score'] = NO
        self.options['apgar_score_min_5'] = 3
        form_validator = BirthDataFormValidator(
            cleaned_data=self.options)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('apgar_score_min_5', form_validator._errors)

    def test_validate_apgar_6(self):
        self.options['apgar_score'] = NO
        self.options['apgar_score_min_1'] = 3
        form_validator = BirthDataFormValidator(
            cleaned_data=self.options)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('apgar_score_min_1', form_validator._errors)

    def test_validate_apgar_7(self):
        self.options['apgar_score'] = YES
        self.options['apgar_score_min_1'] = 2
        self.options['apgar_score_min_5'] = 3
        self.options['apgar_score_min_10'] = 4
        form_validator = BirthDataFormValidator(
            cleaned_data=self.options)
        try:
            form_validator.validate()
        except ValidationError as e:
            self.fail(f'ValidationError unexpectedly raised. Got{e}')

    def test_gestational_age_required(self):
        self.options['gestational_age'] = None
        
        form_validator = BirthDataFormValidator(
            cleaned_data=self.options
        )
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('gestational_age', form_validator._errors)

    def test_gestational_age_4_is_invalid(self):
        """
        If gestational_age is less than 22 or more than 43, 
        an exception should be raised or otherwise
        """
        self.options['gestational_age'] = 4

        form_validator = BirthDataFormValidator(
            cleaned_data=self.options
        )

        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('gestational_age', form_validator._errors)

    def test_gestational_age_24_is_valid(self):
        """
        If gestational_age is less than 22 or more than 43,
        an exception should be raised or otherwise
        """
        self.options['gestational_age'] = 24

        form_validator = BirthDataFormValidator(
            cleaned_data=self.options
        )

        try:
            form_validator.validate();
        except ValidationError:
            self.fail(f"gestational_age: {self.options['gestational_age']} "
                      "not between 22 and 44")
