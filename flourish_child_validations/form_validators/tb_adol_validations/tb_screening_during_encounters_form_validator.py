from edc_form_validators import FormValidator
from edc_constants.constants import OTHER, YES
from ..form_validator_mixin import ChildFormValidatorMixin


class TbScreeningDuringEncountersFormValidator(ChildFormValidatorMixin, FormValidator):

    def clean(self):
        super().clean()

        self.m2m_other_specify(OTHER,
                               m2m_field='care_location',
                               field_other='care_location_other')

        self.required_if_not_none(
            field='care_location',
            field_required='visit_reason'
        )

        self.validate_other_specify(
            field='visit_reason',
            other_specify_field='visit_reason_other'
        )

        self.required_if(YES,
                         field='screening_questions',
                         field_required='pos_screen')

        self.required_if(YES,
                         field='pos_screen',
                         field_required='diagnostic_referral')

        self.required_if(YES,
                         field='diagnostic_referral',
                         field_required='diagnostic_studies')

        self.validate_other_specify(
            field='diagnostic_studies',
            other_specify_field='diagnostic_studies_other'
        )

        self.required_if_not_none(field='diagnostic_studies',
                                  field_required='tb_diagnostic')

        self.required_if(YES,
                         field='tb_diagnostic',
                         field_required='specify_tests')
