from django.core.exceptions import ValidationError
from edc_constants.constants import YES, NO, NOT_APPLICABLE
from edc_form_validators import FormValidator

from .form_validator_mixin import ChildFormValidatorMixin


class ChildMedicalHistoryFormValidator(ChildFormValidatorMixin, FormValidator):

    def clean(self):

        self.subject_identifier = self.cleaned_data.get(
            'child_visit').appointment.subject_identifier

        self.chronic_illness_validations()
        self.current_illness_validations()
        self.current_medication_validations()

        self.required_if(YES,
                         field='had_op_visit',
                         field_required='op_visit_count')

        super().clean()

    def chronic_illness_validations(self):

        chronic_since = self.cleaned_data.get('chronic_since')
        child_chronic = self.cleaned_data.get('child_chronic')

        self.not_applicable_not_allowed('chist_na',
                                        field=chronic_since,
                                        m2m_field=child_chronic)

        self.m2m_single_selection_if('chist_na', m2m_field='child_chronic')

        self.m2m_other_specify('chist_other',
                               m2m_field='child_chronic',
                               field_other='child_chronic_other')

    def current_illness_validations(self):
        self.m2m_required_if(YES,
                             field='current_illness',
                             m2m_field='current_symptoms')

        self.m2m_other_specify(
            'child_sx_other',
            m2m_field='current_symptoms',
            field_other='current_symptoms_other')

        for field in ['symptoms_start_date', 'seen_at_local_clinic']:
            self.required_if(YES,
                             field='current_illness',
                             field_required=field)

    def current_medication_validations(self):

        self.m2m_required_if(
            YES,
            field='currently_taking_medications',
            m2m_field='current_medications')

        self.m2m_other_specify(
            'child_med_other',
            m2m_field='current_medications',
            field_other='current_medications_other')

        self.required_if(YES,
                         field='currently_taking_medications',
                         field_required='duration_of_medications')

    def not_applicable_not_allowed(self, *selections, field=None, m2m_field=None):

        if m2m_field and field:
            selected = {obj.short_name: obj.name for obj in m2m_field if
                        m2m_field is not None}
            if field == YES and m2m_field:
                for selection in selections:
                    if selection in selected:
                        message = {'child_chronic': 'This field is applicable'}
                        self._errors.update(message)
                        raise ValidationError(message)
            elif field in [NO, NOT_APPLICABLE]:
                if 'chist_na' not in selected:
                    message = {
                        'child_chronic': 'You can only select \'Not Applicable\''}
                    self._errors.update(message)
                    raise ValidationError(message)
