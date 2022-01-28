from django.core.exceptions import ValidationError
from django.test import TestCase, tag
from edc_constants.constants import NO, YES, OTHER

from ..form_validators import AdmissionsReasonFormValidations
from ..form_validators import ChildHospitalizationFormValidations


@tag('hoz')
class TestChildHospitalizationForm(TestCase):

    def test_hospitalization_number_not_required_valid(self):
        """
        Raise an error if the hospitalisation number is entered when
        the participant was not hospitalized
        """

        cleaned_data = {
            'hospitalized': YES,
            'number_hospitalised': 2
        }

        form_validator = ChildHospitalizationFormValidations(cleaned_data=cleaned_data)
        try:
            form_validator.validate()
        except ValidationError as e:
            self.fail(f'ValidationError unexpectedly raised. Got{e}')

    def test_hospitalization_number_required_invalid(self):
        """
        Raise an error if the hospitalisation number is entered when
        the participant was not hospitalized
        """

        cleaned_data = {
            'hospitalized': NO,
            'number_hospitalised': 2
        }

        form_validator = ChildHospitalizationFormValidations(cleaned_data=cleaned_data)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('number_hospitalised', form_validator._errors)


@tag('hoz1')
class TestAdmissionsReasonForm(TestCase):

    def test_hospital_name_required_invalid(self):
        """
        Raise an error if the hospital name other is not captured.
        """

        cleaned_data = {
            'hospital_name': OTHER,
            'hospital_name_other': None
        }

        form_validator = AdmissionsReasonFormValidations(cleaned_data=cleaned_data)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('hospital_name_other', form_validator._errors)

    def test_hospital_name_required_valid(self):

        cleaned_data = {
            'hospital_name': OTHER,
            'hospital_name_other': 'blah blah'
        }

        form_validator = AdmissionsReasonFormValidations(cleaned_data=cleaned_data)
        try:
            form_validator.validate()
        except ValidationError as e:
            self.fail(f'ValidationError unexpectedly raised. Got{e}')

    def test_reason_required_invalid(self):
        """
        Raise an error if the reason other is not captured.
        """

        cleaned_data = {
            'reason': OTHER,
            'reason_other': None
        }

        form_validator = AdmissionsReasonFormValidations(cleaned_data=cleaned_data)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('reason_other', form_validator._errors)

    def test_reason_required_valid(self):

        cleaned_data = {
            'reason': OTHER,
            'reason_other': 'blah blah'
        }

        form_validator = AdmissionsReasonFormValidations(cleaned_data=cleaned_data)
        try:
            form_validator.validate()
        except ValidationError as e:
            self.fail(f'ValidationError unexpectedly raised. Got{e}')

    def test_surgical_reason_invalid(self):
        """
        Raise an error if the surgical reason is not captured.
        """

        cleaned_data = {
            'reason': 'surgical',
            'reason_surgical': None
        }

        form_validator = AdmissionsReasonFormValidations(cleaned_data=cleaned_data)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('reason_surgical', form_validator._errors)

    def test_surgical_reason_valid(self):

        cleaned_data = {
            'reason': 'surgical',
            'reason_surgical': 'blah blah'
        }

        form_validator = AdmissionsReasonFormValidations(cleaned_data=cleaned_data)
        try:
            form_validator.validate()
        except ValidationError as e:
            self.fail(f'ValidationError unexpectedly raised. Got{e}')

