from django.forms import ValidationError
from edc_constants.constants import NO, NONE, OTHER, YES, POS, NEG
from edc_form_validators import FormValidator

from .form_validator_mixin import ChildFormValidatorMixin


class ChildTBScreeningFormValidator(ChildFormValidatorMixin, FormValidator):

    def clean(self):
        super().clean()

        self.validate_results_tb_treatment_and_prevention()
    

        required_fields = ['cough', 'fever', 'sweats', 'weight_loss']

        for field in required_fields:
            self.required_if(YES,
                             field=field,
                             field_required=f'{field}_duration')

        self.applicable_if_true(
            self.child_age <= 12,
            field_applicable='fatigue_or_reduced_playfulness',
            applicable_msg=(f'Child age is {self.child_age}, '
                            'question is required for children ≤ 12'),
            not_applicable_msg=(f'Child age is {self.child_age}, '
                                'question is only for children ≤ 12'))

        self.required_if(YES,
                         field='evaluated_for_tb',
                         field_required='flourish_referral')
        
        self.not_flourish_referral_validation()

        field_responses = {
            'chest_xray': 'chest_xray_results',
            'sputum_sample': 'sputum_sample_results',
            'stool_sample': 'stool_sample_results',
            'urine_test': 'urine_test_results',
            'skin_test': 'skin_test_results',
            'blood_test': 'blood_test_results',
        }

        for response, field in field_responses.items():
            self.m2m_other_specify(
                response,
                m2m_field='tb_tests',
                field_other=field,
            )
        
        self.m2m_single_selection_if(
            'None', m2m_field='tb_tests'
        )

        self.m2m_other_specify(
            OTHER,
            m2m_field='tb_tests',
            field_other='other_test',
        )

        self.diagnoses_required_validation()   
             
        self.required_if(YES,
                         field='child_diagnosed_with_tb',
                         field_required='child_on_tb_treatment')

        self.required_if(NO,
                         field='child_diagnosed_with_tb',
                         field_required='child_on_tb_preventive_therapy')

        self.field_cannot_be(field_1='child_diagnosed_with_tb',
                             field_2='child_on_tb_preventive_therapy',
                             field_one_condition=YES,
                             field_two_condition=YES)

        self.validate_other_specify(
            field='child_diagnosed_with_tb',
        )

        self.validate_other_specify(
            field='child_on_tb_treatment',
        )

        self.validate_other_specify(
            field='child_on_tb_preventive_therapy',
        )

    def validate_results_tb_treatment_and_prevention(self):
        child_on_tb_treatment = self.cleaned_data.get('child_on_tb_treatment')
        test_results = [
            self.cleaned_data.get('chest_xray_results'),
            self.cleaned_data.get('sputum_sample_results'),
            self.cleaned_data.get('urine_test_results'),
            self.cleaned_data.get('skin_test_results'),
            self.cleaned_data.get('blood_test_results'),
            self.cleaned_data.get('stool_sample_results'),
        ]

        any_positive = POS in test_results
        all_negative = all(result == NEG for result in test_results)


        if any_positive:
            if child_on_tb_treatment != YES:
                raise ValidationError({
                    'child_on_tb_treatment': 'If any test result is positive, this field must be Yes',
                })
        if all_negative:
            if child_on_tb_treatment != NO :
                raise ValidationError({
                    'child_on_tb_treatment': 'If all test results are negative, this field must not be Yes or Other.',
                    })    

    def field_cannot_be(self, field_1, field_2, field_one_condition,
                        field_two_condition):
        """Raises an exception based on the condition between field_1 and field_2
        values."""
        cleaned_data = self.cleaned_data
        field_1_value = cleaned_data.get(field_1)
        field_2_value = cleaned_data.get(field_2)

        if field_1_value == field_one_condition and field_2_value == field_two_condition:
            message = {field_2: (f'cannot be {field_two_condition} when '
                                 f'is {field_two_condition}.')}
            raise ValidationError(message, code='message')
        return False
    

    def diagnoses_required_validation(self):

        tb_tests_responses = [obj.short_name for obj in self.cleaned_data.get('tb_tests', [])]
        self.required_if_true(any(response != 'None' for response in tb_tests_responses),
                              field_required='child_diagnosed_with_tb')


    def not_flourish_referral_validation(self):
        referral_fields = ['clinic_visit_date','tb_tests','child_diagnosed_with_tb','child_on_tb_treatment',]
    
        for referral_field in referral_fields:

                self.required_if(NO,
                                field='flourish_referral',
                                field_required=referral_field)



