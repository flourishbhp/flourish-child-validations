from django.forms import ValidationError
from edc_constants.constants import NO, OTHER, YES
from edc_form_validators import FormValidator

from .form_validator_mixin import ChildFormValidatorMixin


class ChildTBScreeningFormValidator(ChildFormValidatorMixin, FormValidator):

    def clean(self):
        super().clean()

        required_fields = ['cough', 'fever', 'sweats', 'weight_loss']

        for field in required_fields:
            self.required_if(YES,
                             field=field,
                             field_required=f'{field}_duration')

        self.required_if(YES,
                         field='evaluated_for_tb',
                         field_required='clinic_visit_date')

        field_responses = {
            'chest_xray': 'chest_xray_results',
            'sputum_sample': 'sputum_sample_results',
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

        self.m2m_required_if(
            YES,
            m2m_field='tb_tests',
            field='evaluated_for_tb',
        )

        self.m2m_other_specify(
            OTHER,
            m2m_field='tb_tests',
            field_other='other_test',
        )

        self.m2m_other_specify(
            'none',
            m2m_field='tb_tests',
            field_other='child_diagnosed_with_tb',
        )

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

    def field_cannot_be(self, field_1, field_2, field_one_condition,
                        field_two_condition):
        """Raises an exception based on the condition between field_1 and field_2
        values."""
        cleaned_data = self.cleaned_data
        field_1_value = cleaned_data.get(field_1)
        field_2_value = cleaned_data.get(field_2)

        if field_1_value == field_one_condition and field_2_value == field_two_condition:
            message = {field_2: f'cannot be {field_two_condition} when '
                                f'is {field_two_condition}.'}
            raise ValidationError(message, code='message')
        return False
