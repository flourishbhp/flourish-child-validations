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

        feeding_after_delivery = self.cleaned_data.get('feeding_after_delivery')

        formulafeed_start_dt = self.cleaned_data.get('formulafeed_start_dt')

        feeding_cond = feeding_after_delivery == 'Formula feeding only' or \
            feeding_after_delivery == 'Both breastfeeding and formula feeding'

        self.required_if_not_none(field='breastfeed_start_dt',
                                  field_required='breastfeed_start_est',)

        self.required_if_true(feeding_cond,
                              field_required='formulafeed_start_dt')

        feeding_cond = feeding_cond and formulafeed_start_dt != ''

        self.required_if_true(feeding_cond,
                              field_required='formulafeed_start_est')

