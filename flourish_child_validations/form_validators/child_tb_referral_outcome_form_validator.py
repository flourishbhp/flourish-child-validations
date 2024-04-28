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

        self.make_field_required_if_contains(
            response='Sputum sample',
            field_required='sputum_sample_results',
            field_contains='tests_performed'
        )

        self.make_field_required_if_contains(
            response='other',
            field_contains='tests_performed',
            field_required='other_test_specify'
        )
        self.make_field_required_if_contains(
            response='Chest Xray',
            field_required='chest_xray_results',
            field_contains='tests_performed'
        )

        self.make_field_required_if_contains(
            response='Chest Xray',
            field_required='chest_xray_results',
            field_contains='tests_performed'
        )

        self.make_field_required_if_contains(
            response='Stool sample',
            field_required='stool_sample_results',
            field_contains='tests_performed'
        )

        self.make_field_required_if_contains(
            response='Urine test',
            field_required='urine_test_results',
            field_contains='tests_performed'
        )

        self.make_field_required_if_contains(
            response='Skin test',
            field_required='skin_test_results',
            field_contains='tests_performed'
        )

        self.make_field_required_if_contains(
            response='Blood test',
            field_required='blood_test_results',
            field_contains='tests_performed'
        )

        self.make_field_required_if_contains(
            response='other',
            field_required='other_test_results',
            field_contains='tests_performed'
        )

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

    def make_field_required_if_contains(self, field_contains=None, field_required=None,
                                        response=None, required_msg=None):
        """
        Makes a field required if another field contains a certain value.

        Parameters:
        - field_contains: The field to check for the value.
        - field_required: The field to make required.
        - response: The value that triggers the requirement.
        - required_msg: Optional custom error message if the field is required.

        Returns:
        - False if no error is raised.
        """
        queryset = self.cleaned_data.get(field_contains)
        if queryset:
            value_exists = any(response in str(item) for item in queryset)
            was_none_selected = any('None' in str(item) for item in queryset)
            if was_none_selected and self.cleaned_data.get(field_required):
                message = {field_required: required_msg or 'This field is not required '
                                                           'as none has been selected.'}
                self._errors.update(message)
                self._error_codes.append(NOT_REQUIRED_ERROR)
                raise ValidationError(message, code=NOT_REQUIRED_ERROR)
            if value_exists:
                if not self.cleaned_data.get(field_required):
                    message = {field_required: required_msg or 'This field is required.'}
                    self._errors.update(message)
                    self._error_codes.append(REQUIRED_ERROR)
                    raise ValidationError(message, code=REQUIRED_ERROR)
        return False
