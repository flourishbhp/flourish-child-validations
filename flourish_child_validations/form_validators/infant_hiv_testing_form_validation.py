from edc_form_validators import FormValidator
from edc_constants.choices import YES, NO, OTHER
from .form_validator_mixin import ChildFormValidatorMixin
from django.forms import ValidationError


class InfantHIVTestingFormValidator(ChildFormValidatorMixin, FormValidator):

    def clean(self):
        super().clean()

        self.required_if(
            YES,
            field='child_tested_for_hiv',
            field_required='child_test_date',
        )

        self.required_if_not_none(
            field='child_test_date',
            field_required='child_test_date_estimated',
        )

        self.required_if(
            YES,
            field='child_tested_for_hiv',
            field_required='results_received',
        )

        self.required_if(
            YES,
            field='results_received',
            field_required='recall_result_date',
        )

        self.required_if(
            YES,
            field='recall_result_date',
            field_required='received_date',
        )

        self.required_if_not_none(
            field='received_date',
            field_required='result_date_estimated',
        )

        self.required_if_not_none(
            field='result_date_estimated',
            field_required='hiv_test_result',
        )

        self.required_if(
            YES,
            field='results_received',
            field_required='hiv_test_result',
        )

        self.required_if(
            NO,
            field='child_tested_for_hiv',
            field_required='reason_child_not_tested',
        )

        self.validate_other_specify(
            field='reason_child_not_tested',
            other_specify_field='reason_child_not_tested_other',
        )

        self.required_if(
            NO,
            field='child_tested_for_hiv',
            field_required='preferred_clinic_for_testing',
        )

        self.required_if(
            OTHER,
            field='reason_child_not_tested',
            field_required='reason_child_not_tested_other',
        )

        self.required_if(
            *[OTHER, 'no_testing'],
            field='preferred_clinic_for_testing',
            field_required='additional_comments',
        )

        self.validate_test_date()

    def validate_test_date(self):
        child_test_date = self.cleaned_data.get('child_test_date')
        received_date = self.cleaned_data.get('received_date')

        if child_test_date and received_date and child_test_date > received_date:
            raise ValidationError(
                {'received_date':
                     'Received date cannot be before test date.'})
