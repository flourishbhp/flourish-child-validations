from django.core.exceptions import ValidationError
from django.test import TestCase, tag
from edc_constants.constants import YES, NO, OTHER

from ..form_validators import TbReferralOutcomesFormValidator
from .models import ListModel
from .test_model_mixin import TestModeMixin


@tag('tbrof')
class TestTbReferralOutcomesFormValidator(TestModeMixin, TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(TbReferralOutcomesFormValidator, *args, **kwargs)

    def test_tb_eval_location_required_valid(self):
        """
        Raise error if tb eval is Yes and field tb eval location is not provided
        """
        ListModel.objects.create(short_name="sputum")
        cleaned_data = {
            'tb_eval': YES,
            'tb_eval_location': None,
            'tb_diagnostic_perf': YES,
            'tb_treat_start': NO,
            'tb_prev_therapy_start': YES,
            'tb_diagnose_pos': YES,
            'tb_test_results': "thiiis ",
            'tb_diagnostics': ListModel.objects.all()
        }

        form_validator = TbReferralOutcomesFormValidator(
            cleaned_data=cleaned_data)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('tb_eval_location', form_validator._errors)

    def test_tb_eval_location_other_required_valid(self):
        """
        Raise error if tb eval location is other and field tb eval location other is not provided
        """
        ListModel.objects.create(short_name="sputum")
        cleaned_data = {
            'tb_eval': YES,
            'tb_eval_location': OTHER,
            'tb_eval_location_other': None,
            'tb_diagnostic_perf': YES,
            'tb_treat_start': NO,
            'tb_prev_therapy_start': YES,
            'tb_diagnose_pos': YES,
            'tb_test_results': "thiiis ",
            'tb_diagnostics': ListModel.objects.all()
        }

        form_validator = TbReferralOutcomesFormValidator(
            cleaned_data=cleaned_data)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('tb_eval_location_other', form_validator._errors)

    def test_tb_diag_perf_treat_start_required(self):
        """
        Raise error if tb_diag is No and field tb_treat_start is null
        """
        ListModel.objects.create(short_name="sputum")
        cleaned_data = {
            'tb_eval': YES,
            'tb_eval_location': "Place",
            'tb_eval_location_other': None,
            'tb_diagnostic_perf': NO,
            'tb_treat_start': None,
            'tb_prev_therapy_start': YES,
            'tb_test_results': "thiiis ",
        }

        form_validator = TbReferralOutcomesFormValidator(
            cleaned_data=cleaned_data)

        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('tb_treat_start', form_validator._errors)

    def test_tb_diagnostics_other_specify(self):
        """
         Raise error if tb_diagnostics is Other and tb_diagnostics_other is null
         """
        ListModel.objects.create(short_name=OTHER)
        cleaned_data = {
            'tb_eval': YES,
            'tb_eval_location': "place",
            'tb_eval_location_other': None,
            'tb_diagnostic_perf': YES,
            'tb_treat_start': NO,
            'tb_prev_therapy_start': YES,
            'tb_diagnose_pos': YES,
            'tb_test_results': "thiiis ",
            'tb_diagnostics': ListModel.objects.all()
        }
        form_validator = TbReferralOutcomesFormValidator(
            cleaned_data=cleaned_data)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('tb_diagnostics_other', form_validator._errors)

    def test_referral_tb_diagnostic_perf_not_required(self):
        """
        Raise error if tb_diagnostic_perf is NO and tb_diagnose_pos is provided
        """
        ListModel.objects.create(short_name="sputum")
        cleaned_data = {
            'tb_eval': YES,
            'tb_eval_location': "place",
            'tb_eval_location_other': None,
            'tb_diagnostic_perf': NO,
            'tb_treat_start': NO,
            'tb_prev_therapy_start': YES,
            'tb_diagnose_pos': YES,
            'tb_test_results': "thiiis ",
        }

        form_validator = TbReferralOutcomesFormValidator(
            cleaned_data=cleaned_data)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('tb_diagnose_pos', form_validator._errors)

    def test_referral_tb_diagnostic_perf_required(self):
        """
        Raise error if tb_diagnostic_perf is Yes and tb_diagnose_pos is not provided
        """
        ListModel.objects.create(short_name="sputum")
        cleaned_data = {
            'tb_eval': YES,
            'tb_eval_location': "place",
            'tb_eval_location_other': None,
            'tb_diagnostic_perf': YES,
            'tb_treat_start': NO,
            'tb_prev_therapy_start': YES,
            'tb_diagnostics': ListModel.objects.all(),
            'tb_diagnose_pos': None,
            'tb_test_results': "thiiis ",
        }

        form_validator = TbReferralOutcomesFormValidator(
            cleaned_data=cleaned_data)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('tb_diagnose_pos', form_validator._errors)

    def test_tb_treat_start_required(self):
        """
        Raise error if tb_diagnostic_perf is No and tb_treat_start is not provided
        """
        ListModel.objects.create(short_name="sputum")
        cleaned_data = {
            'tb_eval': YES,
            'tb_eval_location': "place",
            'tb_eval_location_other': None,
            'tb_diagnostic_perf': NO,
            'tb_diagnostics': None,
            'tb_diagnose_pos': None,
            'tb_test_results': None,
            'tb_treat_start': None,
            'tb_prev_therapy_start': None,
        }

        form_validator = TbReferralOutcomesFormValidator(
            cleaned_data=cleaned_data)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('tb_treat_start', form_validator._errors)

    def test_tb_diagnose_pos_tb_treat_start_required(self):
        """
        Raise error if tb_diagnose_pos is No and tb_treat_start is not provided
        """
        ListModel.objects.create(short_name="sputum")
        cleaned_data = {
            'tb_eval': YES,
            'tb_eval_location': "place",
            'tb_eval_location_other': None,
            'tb_diagnostic_perf': YES,
            'tb_diagnostics': ListModel.objects.all(),
            'tb_diagnose_pos': NO,
            'tb_test_results': None,
            'tb_treat_start': YES,
            'tb_prev_therapy_start': None,
        }

        form_validator = TbReferralOutcomesFormValidator(
            cleaned_data=cleaned_data)
        try:
            form_validator.validate()
        except ValidationError as e:
            self.fail(f'ValidationError unexpectedly raised. Got{e}')

    def test_tb_diagnose_pos_tb_treat_start_required_alternate(self):
        """
        Raise error if tb_diagnose_pos is No and tb_treat_start is not provided
        """
        ListModel.objects.create(short_name="sputum")
        cleaned_data = {
            'tb_eval': YES,
            'tb_eval_location': "place",
            'tb_eval_location_other': None,
            'tb_diagnostic_perf': YES,
            'tb_diagnostics': ListModel.objects.all(),
            'tb_diagnose_pos': YES,
            'tb_test_results': "Test",
            'tb_treat_start': YES,
            'tb_prev_therapy_start': None,
        }

        form_validator = TbReferralOutcomesFormValidator(
            cleaned_data=cleaned_data)
        try:
            form_validator.validate()
        except ValidationError as e:
            self.fail(f'ValidationError unexpectedly raised. Got{e}')

    def test_tb_not_evalaluated(self):
        """
        Raise error if tb_diagnose_pos is No and tb_treat_start is not provided
        """
        ListModel.objects.create(short_name="sputum")
        cleaned_data = {
            'tb_eval': NO,
            'tb_treat_start': YES,
            'tb_prev_therapy_start': None,
        }

        form_validator = TbReferralOutcomesFormValidator(
            cleaned_data=cleaned_data)
        try:
            form_validator.validate()
        except ValidationError as e:
            self.fail(f'ValidationError unexpectedly raised. Got{e}')
