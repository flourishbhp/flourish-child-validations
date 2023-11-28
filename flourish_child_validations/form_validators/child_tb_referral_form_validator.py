from edc_constants.constants import YES
from edc_form_validators import FormValidator

from .form_validator_mixin import ChildFormValidatorMixin


class ChildTBReferralFormValidator(ChildFormValidatorMixin, FormValidator):

    def clean(self):
        fields = [
            'date_of_referral',
            'reason_for_referral',
            'clinic_name',
        ]

        for field in fields:
            self.required_if(
                YES,
                field=field,
                field_required='referred_for_screening', )

        self.validate_other_specify(
            field='reason_for_referral',
            other_specify_field='reason_for_referral_other')

        self.validate_other_specify(
            field='clinic_name',
            other_specify_field='clinic_name_other')
