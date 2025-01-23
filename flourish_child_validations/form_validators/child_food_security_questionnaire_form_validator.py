from django.core.exceptions import ValidationError
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

        respondent = self.cleaned_data.get('answerer')
        condition = (respondent == 'child_adolescent' and self.child_age < 10)
        _message = 'Child/Adolescent cannot answer, they are less than 10 years.'

        self.raise_on_selection_condition(condition,
                                          'answerer',
                                          _message)

        self.required_if(
            'both',
            field='answerer',
            field_required='both_respondents_details',
            required_msg=('Details on which questions were responded by who, '
                          'are required if `Both` was selected.'))

    def raise_on_selection_condition(self, condition, field, message):
        if condition:
            msg = {field: message}
            self._errors.update(msg)
            raise ValidationError(msg)
