from django.forms import ValidationError
from edc_constants.constants import NO, YES, OTHER
from edc_form_validators import FormValidator

from .form_validator_mixin import ChildFormValidatorMixin


class ChildReferralFUFormValidator(ChildFormValidatorMixin, FormValidator):

    def clean(self):
        self.subject_identifier = self.cleaned_data.get(
            'child_visit').appointment.subject_identifier

        super().clean()

        self.validate_consent_version_obj(self.subject_identifier)

        self.validate_other_specify(field='percieve_counselor')

        self.required_if(NO,
                         field='satisfied_counselor',
                         field_required='additional_counseling')

        if self.cleaned_data.get('attended_referral'):
            self.referral_specific_validations()

        if self.cleaned_data.get('emo_support_provider'):
            self.referral_fu_specific_validations()

        self.m2m_other_specify(OTHER,
                               m2m_field='emo_support_type',
                               field_other='emo_support_type_other')

        self.m2m_other_specify(OTHER,
                               m2m_field='emo_health_improved',
                               field_other='emo_health_improved_other')

    def referral_specific_validations(self):

        self.required_if(NO,
                         field='attended_referral',
                         field_required='support_ref_decline_reason')

        self.required_if(YES,
                         field='attended_referral',
                         field_required='emo_support')

        self.m2m_required_if(YES,
                             field='emo_support',
                             m2m_field='emo_support_type')

        other_fields = ['referred_to', 'support_ref_decline_reason',
                        'no_support_reason']

        for other_field in other_fields:
            self.validate_other_specify(field=other_field)

        self.required_if(NO,
                         field='emo_support',
                         field_required='no_support_reason')

        emo_fields = ['percieve_counselor',
                      'satisfied_counselor']

        for emo in emo_fields:
            self.required_if(YES,
                             field='emo_support',
                             field_required=emo)

        self.m2m_required_if(YES,
                             field='emo_support',
                             m2m_field='emo_health_improved')

    def referral_fu_specific_validations(self):

        pnta_fields = ['emo_support_type', 'emo_health_improved',
                       'percieve_counselor', 'satisfied_counselor']

        for p_field in pnta_fields:
            self.not_required_if('PNTA',
                                 field='emo_support_provider',
                                 field_required=p_field)

        self.m2m_not_required_if('PNTA',
                                 field='emo_support_provider',
                                 m2m_field='emo_support_type',)

        self.m2m_not_required_if('PNTA',
                                 field='emo_support_provider',
                                 m2m_field='emo_health_improved',)

    def m2m_not_required_if(self, response=None, field=None, m2m_field=None):
        """Raises an exception or returns False.

        m2m_field is required if field  == response
        """
        message = None
        if (self.cleaned_data.get(field) == response
                and self.cleaned_data.get(m2m_field)):
            message = {m2m_field: 'This field is not required'}
        elif (self.cleaned_data.get(field) == response
              and self.cleaned_data.get(m2m_field).count() != 0):
            message = {m2m_field: 'This field is not required'}
        elif (self.cleaned_data.get(field) != response
              and self.cleaned_data.get(m2m_field)
              and self.cleaned_data.get(m2m_field).count() == 0):
            message = {m2m_field: 'This field is required'}
        if message:
            self._errors.update(message)
            raise ValidationError(message)
        return False
