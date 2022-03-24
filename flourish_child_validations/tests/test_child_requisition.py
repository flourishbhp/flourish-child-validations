from django.core.exceptions import ValidationError
from django.test import TestCase, tag
from edc_constants.constants import YES

from flourish_child_validations.form_validators import ChildRequisitionsFormValidations


@tag('specimen')
class TestChildRequisition(TestCase):

    def test_no_specimen_drawn(self):
        """Raise an error if the hospital name other is not captured.
        """
        cleaned_data = {
            'is_drawn': YES,
            'item_count': None,
            'estimated_volume': None
            }

        form_validator = ChildRequisitionsFormValidations(
            cleaned_data=cleaned_data)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('item_count', form_validator._errors)
