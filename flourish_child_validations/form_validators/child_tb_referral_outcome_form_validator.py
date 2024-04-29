from edc_constants.constants import OTHER, YES, POS
from edc_form_validators import FormValidator
from edc_form_validators.base_form_validator import REQUIRED_ERROR, NOT_REQUIRED_ERROR
from django.forms import ValidationError

from .form_validator_mixin import ChildFormValidatorMixin


class ChildTBReferralOutcomeFormValidator(ChildFormValidatorMixin, FormValidator):

    def clean(self):
        fields = ['clinic_name',
                  'tests_performed',
                  'diagnosed_with_tb']

        queryset = self.cleaned_data.get('tests_performed')
        sputum_value_exists = any('Sputum sample' in str(item) for item in queryset)
        other_value_exists = any('other' in str(item) for item in queryset)
        chest_xray_value_exists = any('Chest Xray' in str(item) for item in queryset)
        stool_value_exists = any('Stool sample' in str(item) for item in queryset)
        urine_value_exists = any('Urine test' in str(item) for item in queryset)
        skin_value_exists = any('Skin test' in str(item) for item in queryset)
        blood_value_exists = any('Blood test' in str(item) for item in queryset)

        self.m2m_single_selection_if('None',
                                     m2m_field='tests_performed')

        self.required_if_true(sputum_value_exists, 'sputum_sample_results')

        self.required_if_true(other_value_exists,
                              'other_test_specify')
        self.required_if_true(other_value_exists, 'other_test_results')
        self.required_if_true(chest_xray_value_exists, 'chest_xray_results')

        self.required_if_true(stool_value_exists, 'stool_sample_results')

        self.required_if_true(urine_value_exists, 'urine_test_results')

        self.required_if_true(skin_value_exists, 'skin_test_results')

        self.required_if_true(blood_value_exists, 'blood_test_results')

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
