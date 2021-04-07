from django.core.exceptions import ValidationError

from edc_constants.constants import YES, NO, OTHER, NOT_APPLICABLE, NONE
from edc_form_validators import FormValidator


class ChildMedicalHistoryFormValidator(FormValidator):

    def clean(self):

        chronic_since = self.cleaned_data.get('chronic_since')
        child_chronic = self.cleaned_data.get('child_chronic')

        self.m2m_single_selection_if(NOT_APPLICABLE, m2m_field='child_chronic')

        self.m2m_other_specify(
            OTHER,
            m2m_field='child_chronic',
            field_other='child_chronic_other')

        self.m2m_single_selection_if(NONE, m2m_field='who')

        self.not_applicable_not_allowed(NOT_APPLICABLE, field=chronic_since,
                                        m2m_field=child_chronic)

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
            elif field == NO:
                if NOT_APPLICABLE not in selected:
                    message = {'child_chronic':
                               'You can only select \'Not Applicable\''}
                    self._errors.update(message)
                    raise ValidationError(message)
