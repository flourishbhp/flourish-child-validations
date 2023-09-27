from django.core.exceptions import ValidationError
from edc_constants.constants import YES, NO, NOT_APPLICABLE, NONE
from edc_form_validators import FormValidator
from .form_validator_mixin import ChildFormValidatorMixin


class ChildMedicalHistoryFormValidator(ChildFormValidatorMixin, FormValidator):

    def clean(self):

        self.subject_identifier = self.cleaned_data.get(
            'child_visit').appointment.subject_identifier

        self.validate_consent_version_obj(self.subject_identifier)
        chronic_since = self.cleaned_data.get('chronic_since')
        child_chronic = self.cleaned_data.get('child_chronic')

        self.m2m_single_selection_if('chist_na', m2m_field='child_chronic')

        self.m2m_other_specify(
            'chist_other',
            m2m_field='child_chronic',
            field_other='child_chronic_other')

        self.m2m_single_selection_if(NONE, m2m_field='who')

        self.not_applicable_not_allowed('chist_na', field=chronic_since,
                                        m2m_field=child_chronic)

        self.validate_other_specify(field='current_symptoms_child')

        illness_fields = ['current_symptoms_child', 'symptoms_start_date_child',
                          'clinic_visit_child']

        for field in illness_fields:
            self.required_if(
                YES,
                field_required=field,
                field='current_illness_child',
            )

        super().clean()

    def not_applicable_not_allowed(self, *selections, field=None, m2m_field=None):

        if m2m_field and field:
            selected = {obj.short_name: obj.name for obj in m2m_field if m2m_field is not None}
            if field == YES and m2m_field:
                for selection in selections:
                    if selection in selected:
                        message = {'child_chronic':
                                   'This field is applicable'}
                        self._errors.update(message)
                        raise ValidationError(message)
            elif field in [NO, NOT_APPLICABLE]:
                if 'chist_na' not in selected:
                    message = {'child_chronic':
                               'You can only select \'Not Applicable\''}
                    self._errors.update(message)
                    raise ValidationError(message)

    def validate_m2m_na(self, m2m_field, na_response='chist_na', message=None):
        qs = self.cleaned_data.get(m2m_field)
        message = message or 'This field is not applicable.'
        if qs and qs.count() > 0:
            selected = {obj.short_name: obj.name for obj in qs}
            if na_response not in selected:
                msg = {m2m_field: message}
                self._errors.update(msg)
                raise ValidationError(msg)

            self.m2m_single_selection_if(
                na_response,
                m2m_field=m2m_field)
