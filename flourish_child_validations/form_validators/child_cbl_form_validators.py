from edc_constants.constants import NO
from edc_form_validators import FormValidator

from flourish_child_validations.form_validators import ChildFormValidatorMixin


class ChildCBCLSection4FormValidator(ChildFormValidatorMixin, FormValidator):

    def clean(self):
        fieds = ['impact_on_responses', 'invalid_reason']
        for field in fieds:
            self.required_if(
                NO, field='valid', field_required=field)


