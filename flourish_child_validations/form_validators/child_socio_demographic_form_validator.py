from edc_form_validators import FormValidator

from .form_validator_mixin import ChildFormValidatorMixin


class ChildSocioDemographicFormValidator(ChildFormValidatorMixin, FormValidator):

    def clean(self):
        super().clean()

        report_datetime = self.cleaned_data.get('report_datetime')

        self.validate_against_visit_datetime(report_datetime)

        other_specify_fields = ['ethnicity', 'toilet_facility']

        for field in other_specify_fields:
            self.validate_other_specify(field=field)
