from edc_constants.constants import NO, YES
from edc_form_validators import FormValidator

from .form_validator_mixin import ChildFormValidatorMixin


def check_values(queryset, values):
    return {value: any(value in str(item) for item in queryset) for value in
            values}


class ChildTBReferralOutcomeFormValidator(ChildFormValidatorMixin, FormValidator):

    def clean(self):
        fields = ['clinic_name',
                  'tests_performed',
                  'diagnosed_with_tb']

        queryset = self.cleaned_data.get('tests_performed')
        value_checks = check_values(queryset,
                                    ['Sputum sample', 'other', 'Chest Xray',
                                     'Stool sample', 'Urine test', 'Skin test',
                                     'Blood test'])

        self.m2m_single_selection_if('none', m2m_field='tests_performed')

        for value, exists in value_checks.items():
            self.required_if_true(exists, f'{value.lower().replace(" ", "_")}_results')
            if value == 'other':
                self.required_if_true(exists, 'other_test_specify')
                self.required_if_true(exists, 'other_test_results')

        for field in fields:
            self.required_if(
                YES,
                field='tb_evaluation',
                field_required=field
            )

        self.validate_other_specify(
            field='clinic_name',
            other_specify_field='clinic_name_other'
        )

        tb_preventative_fields = [
            'tb_preventative_therapy',
            'tb_isoniazid_preventative_therapy',
        ]

        for field in tb_preventative_fields:
            self.required_if(
                YES,
                field='tb_treatment',
                field_required=field
            )

        self.validate_other_specify(
            field='tb_treatment',
            other_specify_field='other_tb_treatment'
        )

        self.validate_other_specify(
            field='tb_preventative_therapy',
            other_specify_field='other_tb_preventative_therapy'
        )

        self.validate_other_specify(
            field='tb_isoniazid_preventative_therapy',
            other_specify_field='other_tb_isoniazid_preventative_therapy'
        )

        self.required_if(
            NO,
            field='tb_evaluation',
            field_required='reasons',
        )
