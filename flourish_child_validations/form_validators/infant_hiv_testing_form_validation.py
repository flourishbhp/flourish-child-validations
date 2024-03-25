from django.forms import ValidationError
from edc_constants.choices import NO, YES
from edc_constants.constants import OTHER
from edc_form_validators import FormValidator

from .form_validator_mixin import ChildFormValidatorMixin


class InfantHIVTestingFormValidator(ChildFormValidatorMixin, FormValidator):

    def clean(self):
        super().clean()

        self.m2m_required_if(
            response=YES,
            field='child_tested_for_hiv',
            m2m_field='test_visit',
        )

        self.required_if(
            NO,
            field='child_tested_for_hiv',
            field_required='not_tested_reason',
        )

        self.m2m_other_specify(
            OTHER,
            m2m_field='reason_child_not_tested',
            field_other='reason_child_not_tested_other',
        )

        self.m2m_other_specify(
            OTHER,
            m2m_field='test_visit',
            field_other='test_visit_other',
        )

        self.validate_other_specify(
            field='pref_location',
            other_specify_field='pref_location_other',
        )


class InfantHIVTestingAdminFormValidatorRepeat(ChildFormValidatorMixin,
                                               FormValidator):

    def clean(self):
        super().clean()
        self.validate_other_specify(
            field='test_location',
            other_specify_field='test_location_other',
        )

        self.required_if(
            YES,
            field='results_received',
            field_required='received_date',
        )

        self.required_if(
            YES,
            field='results_received',
            field_required='result_date_estimated',
        )

        self.required_if(
            YES,
            field='results_received',
            field_required='hiv_test_result',
        )

        self.validate_test_date()

    def validate_test_date(self):
        child_test_date = self.cleaned_data.get('child_test_date', None)
        received_date = self.cleaned_data.get('received_date', None)

        if child_test_date and received_date and child_test_date > received_date:
            raise ValidationError(
                {'received_date': 'Received date cannot be before test date.'})
