from edc_constants.constants import OTHER, YES, POS
from edc_form_validators import FormValidator

from .form_validator_mixin import ChildFormValidatorMixin


class ChildTBReferralOutcomeFormValidator(ChildFormValidatorMixin, FormValidator):

    def clean(self):
        fields = ['clinic_name',
                  'tests_performed',
                  'diagnosed_with_tb']
        breakpoint()
        for field in fields:
            self.required_if(
                YES,
                field='tb_evaluation',
                field_required=field
            )
        breakpoint()
        self.validate_other_specify(
            field='clinic_name',
            other_specify_field='clinic_name_other'
        )

        self.m2m_other_specify(
            m2m_field='tests_performed',
            field_other='other_test_specify'
        )

        self.m2m_required_if(
            response='chest_xray',
            field='chest_xray_results',
            m2m_field='tests_performed'
        )

        self.m2m_required_if(
            response='sputum_sample',
            field='sputum_sample_results',
            m2m_field='tests_performed'
        )

        self.m2m_required_if(
            response='stool_sample',
            field='sputum_sample_results',
            m2m_field='tests_performed'
        )

        self.m2m_required_if(
            response='urine_test',
            field='urine_test_results',
            m2m_field='tests_performed'
        )

        self.m2m_required_if(
            response='skin_test',
            field='skin_test_results',
            m2m_field='tests_performed'
        )

        self.m2m_required_if(
            response='blood_test',
            field='blood_test_results',
            m2m_field='tests_performed'
        )

        self.m2m_required_if(
            response='stool_sample',
            field='stool_sample_results',
            m2m_field='tests_performed'
        )

        self.m2m_required_if(
            response=OTHER,
            field='other_test_results',
            m2m_field='tests_performed'
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
