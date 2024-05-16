from django.core.exceptions import ValidationError
from edc_constants.constants import NO, OTHER, YES, POS, ABNORMAL
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

        tb_diagnostics_other = self.cleaned_data.get('tb_diagnostics_other',
                                                     None)

        self.required_if_true(tb_diagnostics_other,
                              field_required='tb_diagnostics_other_results')

        field_answer_dict = {
            'sputum_sample': 'sputum',
            'chest_xray': 'chest_xray',
            'gene_xpert': 'gene_xpert',
            'tst_or_mentoux': 'tst_mantoux',
            'covid_19': 'covid_19_test'
        }

        for key, value in field_answer_dict.items():
            self.m2m_other_specify(value,
                                   m2m_field='tb_diagnostics',
                                   field_other=key)

        self.validate_tb()

        self.required_if(
            NO,
            field='tb_treat_start',
            field_required='tb_prev_therapy_start'
        )

    def validate_tb(self):
        """
        if all tests are neg, tb_treat_start should be no or vice versa
        for pos results
        """
        sputum_sample = self.cleaned_data.get('sputum_sample', None)
        chest_xray = self.cleaned_data.get('chest_xray', None)
        gene_xpert = self.cleaned_data.get('gene_xpert', None)
        tst_or_mentoux = self.cleaned_data.get('tst_or_mentoux', None)
        covid_19 = self.cleaned_data.get('covid_19', None)
        tb_treat_start = self.cleaned_data.get('tb_treat_start')  # compulsory

        answers = [sputum_sample, chest_xray,
                   gene_xpert, tst_or_mentoux, covid_19]

        answers = list(
            filter(lambda element: element in [POS, ABNORMAL] and element != None, answers))

        if answers and tb_treat_start == NO:
            raise ValidationError(
                {'tb_treat_start': 'Not all tests are negative'})
