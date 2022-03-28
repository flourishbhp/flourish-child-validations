from django.core.exceptions import ValidationError
from edc_constants.constants import NO
from edc_form_validators import FormValidator

from .form_validator_mixin import ChildFormValidatorMixin


class ChildPregTestingFormValidator(ChildFormValidatorMixin, FormValidator):

    def clean(self):
        self.subject_identifier = self.cleaned_data.get(
            'child_visit').appointment.subject_identifier

        test_done = self.cleaned_data.get('test_done')
        if test_done == NO:
            message = {'test_done':
                       'A pregnancy test is needed'}
            self._errors.update(message)
            raise ValidationError(message)

        self.validate_consent_version_obj(self.subject_identifier)
