from edc_form_validators import FormValidator
from edc_constants.constants import YES
from ..form_validator_mixin import ChildFormValidatorMixin


class Covid19AdolFormValidator(ChildFormValidatorMixin, FormValidator):

    def clean(self):
        super().clean()

        self.required_if(YES,
                         field='test_for_covid',
                         field_required='receive_test_result')

        self.required_if(YES,
                         field='receive_test_result',
                         field_required='result_of_test')
