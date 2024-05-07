from edc_form_validators import FormValidator
from edc_constants.constants import YES
from ..form_validator_mixin import ChildFormValidatorMixin


class TbVisitScreeningFormValidator(ChildFormValidatorMixin, FormValidator):

    def clean(self):
        super().clean()

        self.required_if(YES,
                         field='have_cough',
                         field_required='cough_duration')

        self.required_if(YES,
                         field='fever',
                         field_required='fever_duration')
