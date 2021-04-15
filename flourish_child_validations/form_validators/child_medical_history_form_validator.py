from django.core.exceptions import ValidationError

from edc_constants.constants import YES, NO, OTHER, NOT_APPLICABLE, NONE
from edc_form_validators import FormValidator


class ChildMedicalHistoryFormValidator(FormValidator):

    def clean(self):

        chronic_since = self.cleaned_data.get('chronic_since')
        child_chronic = self.cleaned_data.get('child_chronic')

        med_history_changed = self.cleaned_data.get('med_history_changed')
        self.validate_med_history_changed(med_history_changed)
        if not med_history_changed or med_history_changed == YES:
            self.m2m_single_selection_if(NOT_APPLICABLE, m2m_field='child_chronic')

            self.m2m_other_specify(
                OTHER,
                m2m_field='child_chronic',
                field_other='child_chronic_other')

            self.m2m_single_selection_if(NONE, m2m_field='who')

            self.not_applicable_not_allowed(NOT_APPLICABLE, field=chronic_since,
                                            m2m_field=child_chronic)

    def validate_med_history_changed(self, med_history_changed):
        if med_history_changed:
            if med_history_changed == NOT_APPLICABLE:
                msg = {'med_history_changed': 'This field is applicable.'}
                self._errors.update(msg)
                raise ValidationError(msg)

            self.not_applicable_if(
                NO,
                field='med_history_changed',
                field_applicable='chronic_since')

            self.not_required_if(
                NO,
                field='med_history_changed',
                field_required='child_chronic_other',
                inverse=False)

            if med_history_changed == NO:
                m2m_fields = ['child_chronic', 'who']
                for field in m2m_fields:
                    self.validate_m2m_na(field)

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
                if NOT_APPLICABLE not in selected:
                    message = {'child_chronic':
                               'You can only select \'Not Applicable\''}
                    self._errors.update(message)
                    raise ValidationError(message)

    def validate_m2m_na(self, m2m_field, message=None):
        qs = self.cleaned_data.get(m2m_field)
        message = message or 'This field is not applicable.'
        if qs and qs.count() > 0:
            selected = {obj.short_name: obj.name for obj in qs}
            if NOT_APPLICABLE not in selected:
                msg = {m2m_field: message}
                self._errors.update(msg)
                raise ValidationError(msg)

            self.m2m_single_selection_if(
                NOT_APPLICABLE,
                m2m_field=m2m_field)
