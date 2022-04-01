from edc_constants.constants import YES, OTHER
from edc_form_validators import FormValidator
from .form_validator_mixin import ChildFormValidatorMixin


class ChildPreviousHospitalisationFormValidator(ChildFormValidatorMixin, FormValidator):

    def clean(self):
        self.subject_identifier = self.cleaned_data.get(
            'child_visit').appointment.subject_identifier

        self.validate_consent_version_obj(self.subject_identifier)
        self.required_if(YES, field='child_hospitalized',
                         field_required='hospitalized_count')

        self.required_if(YES, field='hos_last_visit',
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
