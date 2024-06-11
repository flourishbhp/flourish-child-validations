from django.core.exceptions import ValidationError
from django.test import tag, TestCase
from django.utils import timezone
from edc_base.utils import get_utcnow
from edc_constants.constants import NO, NOT_APPLICABLE, YES

from .models import Appointment, ChildVisit, RegisteredSubject
from .test_model_mixin import TestModelMixin
from ..form_validators import InfantArvExposureFormValidator


@tag('mm')
class TestInfantArvExposureFormValidator(TestModelMixin, TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(InfantArvExposureFormValidator, *args, **kwargs)

    def setUp(self):
        appointment = Appointment.objects.create(
            subject_identifier='2334432-1',
            appt_datetime=timezone.now(),
            visit_code='2000',
            visit_instance='0')

        self.child_visit = ChildVisit.objects.create(
            subject_identifier=appointment.subject_identifier,
            appointment=appointment)

        RegisteredSubject.objects.create(
            subject_identifier=appointment.subject_identifier,
            relative_identifier='2334432', )

    def test_azt_after_birth_yes_azt_dose_date_required(self):
        cleaned_data = {
            'child_visit': self.child_visit,
            'azt_after_birth': YES,
            'azt_dose_date': None
        }
        form_validator = InfantArvExposureFormValidator(cleaned_data=cleaned_data)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('azt_dose_date', form_validator._errors)

    def test_azt_after_birth_yes_azt_dose_date_provided(self):
        cleaned_data = {
            'child_visit': self.child_visit,
            'azt_after_birth': YES,
            'azt_within_72h': YES,
            'azt_dose_date': get_utcnow().date(),
            'azt_within_72h': 'blah',
            'snvp_dose_within_72h': 'blah'
        }
        form_validator = InfantArvExposureFormValidator(cleaned_data=cleaned_data)
        try:
            form_validator.validate()
        except ValidationError as e:
            self.fail(f'ValidationError raised unepectedly. Got{e}')

    def test_azt_after_birth_no_azt_dose_date_invalid(self):
        cleaned_data = {
            'child_visit': self.child_visit,
            'azt_after_birth': NO,
            'azt_dose_date': get_utcnow().date()
        }
        form_validator = InfantArvExposureFormValidator(cleaned_data=cleaned_data)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('azt_dose_date', form_validator._errors)

    def test_azt_after_birth_no_azt_dose_date_none_valid(self):
        cleaned_data = {
            'child_visit': self.child_visit,
            'azt_after_birth': NO,
            'azt_dose_date': None
        }
        form_validator = InfantArvExposureFormValidator(cleaned_data=cleaned_data)
        try:
            form_validator.validate()
        except ValidationError as e:
            self.fail(f'ValidationError raised unepectedly. Got{e}')

    def test_azt_after_birth_yes_azt_additional_dose_na_invalid(self):
        cleaned_data = {
            'child_visit': self.child_visit,
            'azt_after_birth': YES,
            'azt_within_72h': YES,
            'azt_dose_date': get_utcnow().date(),
            'azt_additional_dose': NOT_APPLICABLE,
            'azt_within_72h': 'blah'
        }
        form_validator = InfantArvExposureFormValidator(cleaned_data=cleaned_data)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('azt_additional_dose', form_validator._errors)

    def test_azt_after_birth_yes_azt_additional_dose_valid(self):
        cleaned_data = {
            'child_visit': self.child_visit,
            'azt_after_birth': YES,
            'azt_within_72h': YES,
            'azt_dose_date': get_utcnow().date(),
            'azt_additional_dose': 'Unknown',
            'azt_within_72h':'blah'
        }
        form_validator = InfantArvExposureFormValidator(cleaned_data=cleaned_data)
        try:
            form_validator.validate()
        except ValidationError as e:
            self.fail(f'ValidationError raised unepectedly. Got{e}')

    def test_azt_after_birth_no_azt_additional_dose_invalid(self):
        cleaned_data = {
            'child_visit': self.child_visit,
            'azt_after_birth': NO,
            'azt_dose_date': None,
            'azt_additional_dose': 'Unknown'
        }
        form_validator = InfantArvExposureFormValidator(cleaned_data=cleaned_data)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('azt_additional_dose', form_validator._errors)

    def test_azt_after_birth_no_azt_additional_dose_na_valid(self):
        cleaned_data = {
            'child_visit': self.child_visit,
            'azt_after_birth': NO,
            'azt_dose_date': None,
            'azt_additional_dose': NOT_APPLICABLE
        }
        form_validator = InfantArvExposureFormValidator(cleaned_data=cleaned_data)
        try:
            form_validator.validate()
        except ValidationError as e:
            self.fail(f'ValidationError raised unepectedly. Got{e}')

    def test_sdnvp_after_birth_yes_nvp_dose_date_required(self):
        cleaned_data = {
            'child_visit': self.child_visit,
            'sdnvp_after_birth': YES,
            'nvp_dose_date': None
        }
        form_validator = InfantArvExposureFormValidator(cleaned_data=cleaned_data)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('nvp_dose_date', form_validator._errors)

    def test_sdnvp_after_birth_yes_nvp_dose_date_provided(self):
        cleaned_data = {
            'child_visit': self.child_visit,
            'sdnvp_after_birth': YES,
            'snvp_dose_within_72h': YES,
            'nvp_dose_date': get_utcnow().date(),
            'snvp_dose_within_72h':'blah'
        }
        form_validator = InfantArvExposureFormValidator(cleaned_data=cleaned_data)
        try:
            form_validator.validate()
        except ValidationError as e:
            self.fail(f'ValidationError raised unepectedly. Got{e}')

    def test_sdnvp_after_birth_no_nvp_dose_date_invalid(self):
        cleaned_data = {
            'child_visit': self.child_visit,
            'sdnvp_after_birth': NO,
            'nvp_dose_date': get_utcnow().date()
        }
        form_validator = InfantArvExposureFormValidator(cleaned_data=cleaned_data)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('nvp_dose_date', form_validator._errors)

    def test_sdnvp_after_birth_no_nvp_dose_date_none_valid(self):
        cleaned_data = {
            'child_visit': self.child_visit,
            'sdnvp_after_birth': NO,
            'nvp_dose_date': None
        }
        form_validator = InfantArvExposureFormValidator(cleaned_data=cleaned_data)
        try:
            form_validator.validate()
        except ValidationError as e:
            self.fail(f'ValidationError raised unepectedly. Got{e}')

    @tag('vnpc')
    def test_validate_nvp_cont_dosing_raises_validation_error(self):
        cleaned_data = {
            'child_visit': self.child_visit,
            'sdnvp_after_birth': NO,
            'nvp_cont_dosing': YES,
        }
        form_validator = InfantArvExposureFormValidator(cleaned_data=cleaned_data)
        self.assertRaises(ValidationError, form_validator.clean)
        self.assertIn('nvp_cont_dosing', form_validator._errors)

    def test_validate_nvp_cont_dosing_no_validation_error(self):
        cleaned_data = {
            'child_visit': self.child_visit,
            'sdnvp_after_birth': YES,
            'nvp_cont_dosing': YES,
            'snvp_dose_within_72h': YES,
            'nvp_dose_date': get_utcnow(),
        }
        form_validator = InfantArvExposureFormValidator(cleaned_data=cleaned_data)
        try:
            form_validator.clean()
        except ValidationError as e:
            self.fail(f'ValidationError raised unexpectedly. Got {e}')
