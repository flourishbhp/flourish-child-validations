from edc_constants.constants import NO, OTHER, YES
from edc_form_validators import FormValidator

from flourish_child_validations.form_validators import ChildFormValidatorMixin


class TbReferralOutcomesFormValidator(ChildFormValidatorMixin, FormValidator):

    def clean(self):
        self.required_if(
            YES,
            field='tb_eval',
            field_required='tb_eval_location'
        )

        self.required_if(
            NO,
            field='tb_eval',
            field_required='reason_not_going'
        )

        self.validate_other_specify(
            field='reason_not_going',
            field_required='reason_not_going_other'
        )

        self.validate_other_specify(
            field='tb_eval_location',
            field_required='tb_eval_location_other'
        )
        self.required_if(
            YES,
            field='tb_eval',
            field_required='tb_diagnostic_perf'
        )

        self.m2m_required_if(
            YES,
            field='tb_diagnostic_perf',
            m2m_field='tb_diagnostics')

        self.m2m_other_specify(
            OTHER,
            m2m_field='tb_diagnostics',
            field_other='tb_diagnostics_other')

        field_answer_dict = {
            'sputum_sample': 'sputum',
            'chest_xray': 'chest_xray',
            'gene_xpert': 'gene_xpert',
            'tst_or_mentoux': 'tst_mantoux',
            'covid_19': 'covid_19_test'
        }

        for key, value in field_answer_dict.items():

            self.m2m_other_specify(key,
                                   m2m_field='tb_diagnostics',
                                   field_other=value)

        self.required_if(
            YES,
            field='tb_diagnostic_perf',
            field_required='tb_diagnose_pos')

        self.required_if(
            YES,
            field='tb_diagnose_pos',
            field_required='tb_test_results')

        self.required_if(
            *[YES, NO],
            field='tb_diagnose_pos',
            field_required='tb_treat_start',
            inverse=False
        )

        self.required_if(
            NO,
            field='tb_diagnostic_perf',
            field_required='tb_treat_start',
            inverse=False
        )

        self.required_if(
            NO,
            field='tb_treat_start',
            field_required='tb_prev_therapy_start')
