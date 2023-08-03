from edc_constants.constants import NO
from edc_form_validators import FormValidator

from flourish_child_validations.form_validators import ChildFormValidatorMixin


class BaseFormValidator(ChildFormValidatorMixin, FormValidator):
    fields_to_validate = []
    validation_criteria = NO
    validation_field = None

    def clean(self):
        for field in self.fields_to_validate:
            self.required_if(
                self.validation_criteria, field=self.validation_field,
                field_required=field
            )


class Brief2ParentFormsValidators(BaseFormValidator):
    fields_to_validate = ['impact_on_responses', 'invalid_reason']
    validation_field = 'valid'


class Brief2SelfReportedFormsValidators(BaseFormValidator):
    fields_to_validate = ['brief2_self_impact_on_responses', 'brief2_self_invalid_reason']
    validation_field = 'brief2_self_valid'
