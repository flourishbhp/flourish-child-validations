from edc_constants.constants import YES, OTHER
from edc_form_validators import FormValidator

from .form_validator_mixin import ChildFormValidatorMixin


class ChildOutpatientFormValidator(ChildFormValidatorMixin, FormValidator):

    def clean(self):
        child_medical_history = self.cleaned_data.get(
            'child_medical_history', None)
        self.subject_identifier = getattr(
            child_medical_history, 'subject_identifier', None)

        super().clean()
        self.required_if(OTHER,
                         field='op_type',
                         field_required='op_type_other')

        self.m2m_required_if('new_illness',
                             field='op_type',
                             m2m_field='op_symptoms')

        self.m2m_other_specify('op_other',
                               m2m_field='op_symptoms',
                               field_other='op_symp_other')

        self.required_if(YES,
                         field='op_new_dx',
                         field_required='op_new_dx_details')

        self.m2m_required_if(YES,
                             field='op_meds_prescribed',
                             m2m_field='op_meds_received')

        self.m2m_other_specify('opmeds_other',
                               m2m_field='op_meds_received',
                               field_other='op_meds_other')

        symptoms = self.cleaned_data.get('op_symptoms', None)
        self.required_if_true(
            symptoms and symptoms.count() > 0,
            field_required='op_symp_resolved')

        self.required_if(YES,
                         field='op_symp_resolved',
                         field_required='op_resolution_dt')
