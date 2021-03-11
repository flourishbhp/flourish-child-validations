from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone
from edc_constants.constants import YES, NO

from ..form_validators import BirthDataFormValidator
from .models import ChildVisit, Appointment


class TestInfantBirthDataFormValidator(TestCase):

    def setUp(self):

        appointment = Appointment.objects.create(
            subject_identifier='2334432',
            appt_datetime=timezone.now(),
            visit_code='2000',
            visit_instance='0')

        child_visit = ChildVisit.objects.create(
            subject_identifier='12345323',
            appointment=appointment)

        self.options = {
            'report_datetime': timezone.now(),
            'child_visit': child_visit,
            'weight_kg': 3.61,
            'infant_length': 89.97,
            'head_circumference': 39.30,
            'apgar_score': NO,
            'apgar_score_min_1': None,
            'apgar_score_min_5': 0,
            'apgar_score_min_10': 0,
            'congenital_anomalities': NO
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
