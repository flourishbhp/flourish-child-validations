from edc_form_validators import FormValidator

from .form_validator_mixin import ChildFormValidatorMixin


class ChildSafiStigmaFormValidator(ChildFormValidatorMixin, FormValidator):

    def clean(self):
        super().clean()
        self.validate_period_required()

    def validate_period_required(self):
        fields = [
            'lost_friends',
            'bullied',
            'home_discr',
            'neighborhood_discr',
            'religious_place_discr',
            'clinic_discr',
            'school_discr',
            'lose_fin_support',
            'lose_social_support',
            'stressed_or_anxious',
            'depressed_or_sad'
        ]

        for field in fields:

            self.required_if(
                'ever_happened',
                field=field,
                field_required=f'{field}_period'
            )

        self.required_if_not_none(
            field='other_place_discr',
            field_required='other_place_discr_period', )
