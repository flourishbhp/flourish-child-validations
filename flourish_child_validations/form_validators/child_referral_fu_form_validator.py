from edc_constants.constants import NO, YES, OTHER
from edc_form_validators import FormValidator

from .form_validator_mixin import ChildFormValidatorMixin


class ChildReferralFUFormValidator(ChildFormValidatorMixin, FormValidator):

    def clean(self):
        self.subject_identifier = self.cleaned_data.get(
            'child_visit').appointment.subject_identifier

        super().clean()

        self.validate_consent_version_obj(self.subject_identifier)

        other_fields = ['referred_to', 'support_ref_decline_reason',
                        'no_support_reason', 'emo_support_type', 'emo_health_improved',
                        'percieve_counselor']

        for other_field in other_fields:
            self.validate_other_specify(field=other_field)

        self.required_if(NO,
                         field='attended_referral',
                         field_required='support_ref_decline_reason')

        self.required_if(YES,
                         field='attended_referral',
                         field_required='emo_support')

        self.required_if(NO,
                         field='emo_support',
                         field_required='no_support_reason')

        self.m2m_required_if(YES,
                             field='emo_support',
                             m2m_field='emo_support_type')

        self.m2m_other_specify(OTHER,
                               m2m_field='emo_support_type',
                               field_other='emo_support_type_other')

        emo_fields = ['emo_health_improved', 'percieve_counselor',
                      'satisfied_counselor']

        for emo in emo_fields:
            self.required_if(YES,
                             field='emo_support',
                             field_required=emo)

        self.required_if(NO,
                         field='satisfied_counselor',
                         field_required='additional_counseling')
