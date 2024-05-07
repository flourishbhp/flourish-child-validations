from django.core.exceptions import ValidationError
from edc_form_validators import FormValidator
from ..form_validator_mixin import ChildFormValidatorMixin


class AnthropometricFormValidator(ChildFormValidatorMixin, FormValidator):

    def clean(self):
        super().clean()

        systolic_bp = self.cleaned_data.get('systolic_bp')
        diastolic_bp = self.cleaned_data.get('diastolic_bp')

        if diastolic_bp > systolic_bp:
            raise ValidationError({
                'diastolic_bp':
                'Diastolic pressure cannot be greater than '
                'systolic pressure', })
