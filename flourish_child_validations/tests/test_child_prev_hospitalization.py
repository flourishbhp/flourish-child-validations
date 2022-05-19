from django.core.exceptions import ValidationError
from django.test import TestCase, tag
from edc_constants.constants import OTHER, YES

from ..form_validators import ChildPreHospitalisationInlineFormValidator, \
    ChildPreviousHospitalisationFormValidator

@tag('hmm')
class TestChildHospitalizationForm(TestCase):

    def test_hospital_count_invalid(self):
        """
        Raise an error if the hospital name other is not captured.
        """
        cleaned_data = {
            'hos_last_visit': YES,
            'hospitalized_count': None
            }

        form_validator = ChildPreviousHospitalisationFormValidator(
            cleaned_data=cleaned_data)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('hospitalized_count', form_validator._errors)


@tag('hozinline')
class TestChildHospitalizationFormInline(TestCase):

    def test_hospital_name_required_invalid(self):
        """
        Raise an error if the hospital name other is not captured.
        """

        cleaned_data = {
            'name_hospital': OTHER,
            'name_hospital_other': 'blah blah'
            }

        form_validator = ChildPreHospitalisationInlineFormValidator(
            cleaned_data=cleaned_data)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('reason_hospitalized', form_validator._errors)

    def test_surgical_reason_valid(self):

        cleaned_data = {
            'reason_hospitalized': OTHER,
            'reason_hospitalized_other': 'surgical',
            'surgical_reason': None
            }

        form_validator = ChildPreHospitalisationInlineFormValidator(
            cleaned_data=cleaned_data)
        try:
            form_validator.validate()
        except ValidationError as e:
            self.fail(f'ValidationError unexpectedly raised. Got{e}')
