from django.forms import ValidationError
from edc_constants.constants import NO, YES, OTHER
from edc_form_validators import FormValidator

from .form_validator_mixin import ChildFormValidatorMixin


class ChildSafiStigmaFormValidator(ChildFormValidatorMixin, FormValidator):

    def clean(self):
        super().clean()
        self.validate_other()
        self.validate_period_required()

    def validate_other(self):
        fields = ['child_other_discrimination_other',
                  'child_other_discrimination_period']

        for field in fields:
            self.required_if('ever_happened',
                             field='child_other_discrimination',
                             field_required=field)

    def validate_period_required(self):
        fields = [
            'lost_friends',
            'discriminated',
            'child_home_discrimination',
            'child_neighborhood_discrimination',
            'child_religious_place_discrimination',
            'child_clinic_discrimination',
            'child_school_discrimination',
            'child_social_effect',
            'child_emotional_effect',
            'child_education_effect',
            'child_future_pespective_changed'
        ]

        for field in fields:

            self.required_if(
                'ever_happened',
                field=field,
                field_required=f'{field}_period'
            )
