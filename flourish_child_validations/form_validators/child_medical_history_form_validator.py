from django.core.exceptions import ValidationError
from edc_constants.constants import YES, NO, NOT_APPLICABLE, NONE, OTHER
from edc_form_validators import FormValidator
from .form_validator_mixin import ChildFormValidatorMixin


class ChildMedicalHistoryFormValidator(ChildFormValidatorMixin, FormValidator):

    def clean(self):

        self.subject_identifier = self.cleaned_data.get(
            'child_visit').appointment.subject_identifier

        self.chronic_illness_validations()
        self.current_illness_validations()
        self.current_medication_validations()

    def chronic_illness_validations(self):
        self.m2m_required_if(YES, field='chronic_since',
                             m2m_field='child_chronic')

        self.m2m_other_specify(m2m_field='child_chronic',
                               field_other='child_chronic_other')

    def current_illness_validations(self):
        self.m2m_required_if(YES, field='current_illness',
                             m2m_field='current_symptoms')

        self.m2m_other_specify(
            OTHER, m2m_field='current_symptoms',
            field_other='current_symptoms_other')

        for field in ['symptoms_start_date', 'seen_at_local_clinic']:
            self.required_if(YES, field='current_illness',
                             field_required=field)

    def current_medication_validations(self):

        self.m2m_required_if(
            YES, field='currently_taking_medications',
            m2m_field='current_medications')

        self.m2m_other_specify(
            OTHER, m2m_field='current_medications',
            field_other='current_medications_other')

        self.required_if(YES,
                         field='currently_taking_medications',
                         field_required='duration_of_medications')
