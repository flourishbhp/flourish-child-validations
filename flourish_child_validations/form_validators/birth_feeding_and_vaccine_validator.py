from edc_form_validators import FormValidator
from ..constants import BREASTFEED_ONLY, BOTH_BREAST_FEEDING_AND_FORMULA, FORMULA_ONLY

from .crf_offstudy_form_validator import CrfOffStudyFormValidator
from .form_validator_mixin import ChildFormValidatorMixin


class BirthFeedingAndVaccineFormValidator(ChildFormValidatorMixin,
                                          CrfOffStudyFormValidator,
                                          FormValidator):

    infant_birth_model = 'flourish_child.childbirth'

    def clean(self):
        self.subject_identifier = self.cleaned_data.get(
            'child_visit').appointment.subject_identifier
        super().clean()

        self.validate_consent_version_obj(self.subject_identifier)

        self.validate_against_visit_datetime(
            self.cleaned_data.get('report_datetime'))

        self.validate_feeding()

        self.validate_breastfeed_dt()

        super().clean()

    def validate_feeding(self):

        feeding_after_delivery = self.cleaned_data.get('feeding_after_delivery')

        breast_feeding_condition = feeding_after_delivery in [BREASTFEED_ONLY,
                                                              BOTH_BREAST_FEEDING_AND_FORMULA]

        formula_feeding_condition = feeding_after_delivery in [FORMULA_ONLY,
                                                               BOTH_BREAST_FEEDING_AND_FORMULA]

        # feeding conditions
        self.required_if_true(condition=breast_feeding_condition,
                              field_required='breastfeed_start_dt')

        self.required_if_true(condition=formula_feeding_condition,
                              field_required='formulafeed_start_dt')

        # required dates
        self.required_if_not_none(field='breastfeed_start_dt',
                                  field_required='breastfeed_start_est')

        self.required_if_not_none(field='formulafeed_start_dt',
                                  field_required='formulafeed_start_est')

    def validate_breastfeed_dt(self):
        breastfeed_start_dt = self.cleaned_data.get('breastfeed_start_dt', None)
        self.validate_against_birth_date(
            infant_identifier=self.subject_identifier,
            report_datetime=breastfeed_start_dt,
            date_attr='dob',
            message='Date when infant breastfeeding began can not be before child DOB.')
