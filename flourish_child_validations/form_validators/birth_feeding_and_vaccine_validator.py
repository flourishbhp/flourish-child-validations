from edc_form_validators import FormValidator

from .crf_offstudy_form_validator import CrfOffStudyFormValidator
from .form_validator_mixin import ChildFormValidatorMixin


class BirthFeedingAndVaccineFormValidator(ChildFormValidatorMixin,
                                          CrfOffStudyFormValidator,
                                          FormValidator):

    def clean(self):
        self.subject_identifier = self.cleaned_data.get(
            'child_visit').appointment.subject_identifier
        super().clean()

        self.validate_against_visit_datetime(
            self.cleaned_data.get('report_datetime'))
