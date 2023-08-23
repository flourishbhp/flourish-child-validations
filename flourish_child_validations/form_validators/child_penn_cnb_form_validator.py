from edc_form_validators import FormValidator

from .form_validator_mixin import ChildFormValidatorMixin
from edc_constants.constants import NO, YES


class ChildPennCNBFormValidator(ChildFormValidatorMixin, FormValidator):

    def clean(self):
        cleaned_data = self.cleaned_data
        self.subject_identifier = self.cleaned_data.get(
            'child_visit').appointment.subject_identifier

        self.validate_consent_version_obj(self.subject_identifier)

        self.required_if(
            NO,
            field='completed',
            field_required='reason_incomplete')

        reason_incomplete = cleaned_data.get('reason_incomplete')
        completed = cleaned_data.get('completed')

        self.required_if_true(
            reason_incomplete == 'handicapped' or completed == NO,
            field_required='comments')

        self.validate_other_specify(
            field='reason_incomplete',
            other_specify_field='reason_other')

        self.validate_other_specify(
            field='testing_impacted',
            other_specify_field='impact_other')

        fields = ['date_deployed', 'start_time', 'stop_time', 'testing_impacted',
                  'claim_experience', 'staff_assisting']

        for field in fields:
            self.required_if(
                YES,
                field='completed',
                field_required=field)
