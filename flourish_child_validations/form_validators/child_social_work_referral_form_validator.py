from edc_form_validators import FormValidator
from flourish_form_validations.form_validators.caregiver_social_work_referral_form_validator import CaregiverSocialWorkReferralFormValidator
from .form_validator_mixin import ChildFormValidatorMixin


class ChildSocialWorkReferralValidator(ChildFormValidatorMixin,
                                       CaregiverSocialWorkReferralFormValidator, FormValidator):

    def clean(self):
        self.subject_identifier = self.cleaned_data.get(
            'child_visit').appointment.subject_identifier

        super().clean()
