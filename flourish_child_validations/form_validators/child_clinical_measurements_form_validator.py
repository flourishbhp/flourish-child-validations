from django.core.exceptions import ValidationError
from edc_form_validators import FormValidator

from .form_validator_mixin import ChildFormValidatorMixin


class ChildClinicalMeasurementsFormValidator(ChildFormValidatorMixin, FormValidator):

    def clean(self):

        cleaned_data = self.cleaned_data
        self.subject_identifier = cleaned_data.get(
            'child_visit').subject_identifier
        super().clean()

        systolic_bp = cleaned_data.get('systolic_bp')
        diastolic_bp = cleaned_data.get('diastolic_bp')

        if systolic_bp and diastolic_bp:
            if systolic_bp < diastolic_bp:
                msg = {'diastolic_bp':
                       'Systolic blood pressure cannot be lower than the '
                       'diastolic blood pressure. Please correct.'}
                self._errors.update(msg)
                raise ValidationError(msg)
