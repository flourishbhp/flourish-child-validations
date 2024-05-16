from edc_form_validators import FormValidator
from edc_constants.constants import YES
from ..form_validator_mixin import ChildFormValidatorMixin


class TbHistoryFormValidator(ChildFormValidatorMixin, FormValidator):

    def clean(self):
        super().clean()

        self.validate_history_of_tbt_required_fields()

        self.validate_prior_tb_history()

    def validate_history_of_tbt_required_fields(self):
        fields = ['reason_for_therapy', 'therapy_prescribed_age', 'tbt_completed']

        for field in fields:
            self.required_if(YES,
                             field='history_of_tbt',
                             field_required=field)

        self.validate_other_specify(
            field='reason_for_therapy',
            other_specify_field='reason_for_therapy_other')

    def validate_prior_tb_history(self):
        fields = ['tb_diagnosis_type', 'tb_drugs_freq',
                  'iv_meds_used', 'tb_treatmnt_completed']

        for field in fields:
            self.required_if(
                YES,
                field='prior_tb_history',
                field_required=field
            )

        self.required_if('outside_the_lungs', 'both',
                         field='tb_diagnosis_type',
                         field_required='extra_pulmonary_loc')

        self.validate_other_specify(
            field='extra_pulmonary_loc',
            other_specify_field='other_loc'
        )

        self.not_required_if('outside_the_lungs', 'both', None,
                             field='tb_diagnosis_type',
                             field_required='prior_treatmnt_history')
