from edc_constants.constants import YES, OTHER
from edc_form_validators import FormValidator


class ChildPreviousHospitalisationFormValidator(FormValidator):

    def clean(self):
        self.required_if(YES, field='child_hospitalized',
                         field_required='hospitalized_count')


class ChildPreHospitalisationInlineFormValidator(FormValidator):

    def clean(self):
        self.validate_other_specify(field='name_hospital',
                                    other_specify_field='name_hospital_other')

        self.m2m_other_specify(OTHER, m2m_field='reason_hospitalized',
                               field_other='reason_hospitalized_other')

        self.m2m_other_specify('surgical_reason',
                               m2m_field='reason_hospitalized',
                               field_other='surgical_reason')
