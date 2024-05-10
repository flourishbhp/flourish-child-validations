from django.forms import ValidationError
from edc_constants.choices import NO, YES
from edc_constants.constants import OTHER
from edc_form_validators import FormValidator

from .form_validator_mixin import ChildFormValidatorMixin


class InfantHIVTestingFormValidator(ChildFormValidatorMixin, FormValidator):
    child_assent_model = 'flourish_child.childassent'
    caregiver_child_consent_model = 'flourish_caregiver.caregiverchildconsent'
    maternal_delivery_model = 'flourish_caregiver.maternaldelivery'

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
            field_required='reason_child_not_tested',
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

        self.validate_test_against_age()

    def check_age(self, age_in_weeks, min_age_months, visit, selected):
        if age_in_weeks < min_age_months and visit in selected:
            raise ValidationError(
                {'test_visit': f'Child is less than {visit}'}
            )

    def validate_test_against_age(self):
        test_visit = self.cleaned_data.get('test_visit')
        selected = {obj.short_name: obj.name for obj in test_visit}
        age_in_weeks = self.child_age * 52

        age_ranges = {
            '6_to_8_weeks': 6,
            '9_months': 9 * 4,
            '18_months': 18 * 4
        }
        for visit, min_age_weeks in age_ranges.items():
            self.check_age(age_in_weeks, min_age_weeks, visit, selected)


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
