from edc_constants.constants import YES
from edc_form_validators import FormValidator


class ChildMedicalHistoryFormValidator(FormValidator):

    def clean(self):

        self.required_if(
            YES,
            field='chronic_since',
            field_required='child_chronic',)
