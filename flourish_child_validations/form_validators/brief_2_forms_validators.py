from edc_constants.constants import NO
from edc_form_validators import FormValidator

from flourish_child_validations.form_validators.form_validator_mixin import \
    ChildFormValidatorMixin


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

    def clean(self):
        super().clean()
        self.validate_other_specify(
            field='invalid_reason',
            other_specify_field='other_invalid_reason',
        )

        self.validate_other_specify(
            field='impact_on_responses',
            other_specify_field='other_impact_on_responses',
        )


class Brief2SelfReportedFormsValidators(BaseFormValidator):
    fields_to_validate = ['brief2_self_impact_on_responses', 'brief2_self_invalid_reason']
    validation_field = 'brief2_self_valid'

    def clean(self):
        super().clean()
        self.validate_other_specify(
            field='brief2_self_invalid_reason',
            other_specify_field='other_breif2_self_invalid_reason',
        )

        self.validate_other_specify(
            field='brief2_self_impact_on_responses',
            other_specify_field='other_brief2_self_impact_on_responses',
        )
