from edc_constants.constants import NO, YES
from edc_form_validators import FormValidator

from .form_validator_mixin import ChildFormValidatorMixin


class ChildPennCNBFormValidator(ChildFormValidatorMixin, FormValidator):

    def clean(self):
        self.subject_identifier = self.cleaned_data.get(
            'child_visit').appointment.subject_identifier

        self.validate_consent_version_obj(self.subject_identifier)

        self.required_if(
            NO,
            field='completed',
            field_required='reason_incomplete')

        self.validate_other_specify(
            field='reason_incomplete',
            other_specify_field='reason_other')

        self.validate_other_specify(
            field='testing_impacted',
            other_specify_field='impact_other')

        fields = ['date_deployed', 'start_time', 'stop_time', 'claim_experience',
                  'staff_assisting', 'laptop_used']

        for field in fields:
            self.required_if(
                YES,
                field='completed',
                field_required=field)
