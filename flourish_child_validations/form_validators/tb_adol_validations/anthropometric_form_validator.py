from django.apps import apps as django_apps
from django.core.exceptions import ValidationError
from edc_form_validators import FormValidator
from edc_constants.constants import OTHER, YES
from ..form_validator_mixin import ChildFormValidatorMixin

class AnthropometricFormValidator(ChildFormValidatorMixin, FormValidator):
      
      
      def clean(self):
        super().clean()
            
        systolic_bp = self.cleaned_data.get('systolic_bp', None)
        diastolic_bp = self.cleaned_data.get('diastolic_bp', None)
        
        if (systolic_bp and diastolic_bp) \
            and (diastolic_bp > systolic_bp):
            raise ValidationError({
                'diastolic_bp': 'Diastolic pressure can never be greater systolic pressure'
            })