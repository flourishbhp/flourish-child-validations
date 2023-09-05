from edc_constants.constants import NO
from edc_form_validators import FormValidator

from flourish_child_validations.form_validators.form_validator_mixin import ChildFormValidatorMixin


class ChildCBCLSection4FormValidator(ChildFormValidatorMixin, FormValidator):

    def clean(self):
        fieds = ['impact_on_responses', 'invalid_reason']
        for field in fieds:
            self.required_if(
                NO, field='valid', field_required=field)

        self.validate_other_specify(
            field='withdrawn',
            other_specify_field='other_withdrawn',
        )

        self.validate_other_specify(
            field='worries',
            other_specify_field='other_worries',
        )


