from edc_constants.constants import YES, NO
from edc_form_validators import FormValidator

from .form_validator_mixin import ChildFormValidatorMixin


class ChildTBReferralFormValidator(ChildFormValidatorMixin, FormValidator):

    def clean(self):
        fields_required = ['date_of_referral', 'reason_for_referral',
                           'clinic_name', 'attend_flourish_clinic']
        for field_required in fields_required:
            self.required_if(YES,
                             field='referred',
                             field_required=field_required)

        self.required_if(NO,
                         field='referred',
                         field_required='no_referral_reason')

        self.validate_other_specify(
            field='reason_for_referral',
            other_specify_field='reason_for_referral_other')

        self.validate_other_specify(
            field='clinic_name',
            other_specify_field='clinic_name_other')

        self.validate_other_specify(
            field='reason_for_referral',
            other_specify_field='reason_for_referral_other')
