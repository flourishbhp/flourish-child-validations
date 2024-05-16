from django.core.exceptions import ValidationError
from edc_constants.constants import FEMALE
from flourish_form_validations.form_validators.social_work_referral_validator_mixin \
    import SocialWorkReferralValidatorMixin

from .form_validator_mixin import ChildFormValidatorMixin


class ChildSocialWorkReferralValidator(ChildFormValidatorMixin,
                                       SocialWorkReferralValidatorMixin):

    def clean(self):
        super().clean()
        self.validate_is_preg()
        self.validate_child_exposure_status()

    def validate_referral_reason(self):
        self.m2m_other_specify('refer_c_other',
                               m2m_field='referral_reason',
                               field_other='reason_other')

        referral_reason = self.cleaned_data.get('referral_reason', [])
        selected = [reason.short_name for reason in referral_reason]
        value_field = {'local_medical_facility': 'comment', }

        for value, field in value_field.items():
            if isinstance(field, list):
                for required in field:
                    self.required_if_true(
                        value in selected,
                        field_required=required)
            else:
                self.required_if_true(
                    value in selected,
                    field_required=field)

    def validate_is_preg(self):
        child_gender = getattr(
            self.child_consent_model_obj, 'gender', None)
        self.required_if_true(
            child_gender == FEMALE,
            field_required='is_preg',
            not_required_msg='Participant is Male, this field is not required')

    def validate_child_exposure_status(self):
        exposure_status = self.cleaned_data.get('child_exposure_status', None)
        cohort_exposure = self.cohort_model_obj().check_exposure()
        child_exposed = cohort_exposure == 'EXPOSED'
        child_unexposed = cohort_exposure == 'UNEXPOSED'
        if (child_exposed and exposure_status != 'heu'):
            raise ValidationError(
                {'child_exposure_status': 'This child is HIV exposed, please correct. '})
        elif child_unexposed and exposure_status != 'huu':
            raise ValidationError(
                {'child_exposure_status': 'This child HIV unexposed, please correct. '})
