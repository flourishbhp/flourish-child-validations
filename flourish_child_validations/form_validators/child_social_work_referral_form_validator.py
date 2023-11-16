from flourish_form_validations.form_validators import SocialWorkReferralValidatorMixin

from .form_validator_mixin import ChildFormValidatorMixin


class ChildSocialWorkReferralValidator(ChildFormValidatorMixin,
                                       SocialWorkReferralValidatorMixin):

    def clean(self):
        self.subject_identifier = self.cleaned_data.get(
            'child_visit').appointment.subject_identifier

        super().clean()

    def validate_referral_reason(self):
        self.m2m_other_specify('refer_c_other',
                               m2m_field='referral_reason',
                               field_other='reason_other')

        referral_reason = self.cleaned_data.get('referral_reason')
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