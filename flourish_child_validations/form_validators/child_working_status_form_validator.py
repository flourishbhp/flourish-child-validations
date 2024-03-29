from edc_form_validators import FormValidator

from .form_validator_mixin import ChildFormValidatorMixin


class ChildWorkingStatusFormValidator(ChildFormValidatorMixin, FormValidator):

    def clean(self):
        super().clean()
        report_datetime = self.cleaned_data.get('report_datetime')

        self.subject_identifier = self.cleaned_data.get(
            'child_visit').appointment.subject_identifier

        self.validate_consent_version_obj(self.subject_identifier)

        self.validate_against_visit_datetime(report_datetime)

        self.validate_other_specify(field='work_type')
