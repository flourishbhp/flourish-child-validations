from edc_constants.constants import YES
from edc_form_validators import FormValidator
from .form_validator_mixin import ChildFormValidatorMixin


class ChildFoodSecurityQuestionnaireFormValidator(ChildFormValidatorMixin, FormValidator):

    def clean(self):
        super().clean()

        self.subject_identifier = self.cleaned_data.get(
            'child_visit').appointment.subject_identifier

        self.validate_consent_version_obj(self.subject_identifier)

        self.required_if(YES,
                         field='cut_meals',
                         field_required='how_often')
