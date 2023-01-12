from django.core.exceptions import ValidationError
from django.test import TestCase, tag
from edc_constants.constants import OTHER

from flourish_child_validations.form_validators import ChildReferralFUFormValidator, \
    InfantFeedingFormValidator
from flourish_child_validations.tests.test_model_mixin import TestModeMixin


class TestInfantBirthDataFormValidator(TestModeMixin, TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(InfantFeedingFormValidator, *args, **kwargs)
    @tag('emo')
    def test_emo_support_type_other(self):
        """
               Raise an error if the emo support type other is not captured.
               """

        cleaned_data = {
            'emo_support_type': OTHER,
            'emo_support_type_other': None
        }

        form_validator = ChildReferralFUFormValidator(
            cleaned_data=cleaned_data)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('emo_support_type_other', form_validator._errors)
