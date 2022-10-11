from django.core.exceptions import ValidationError
from django.test import TestCase, tag
from django.utils import timezone
from edc_base.utils import get_utcnow
from edc_constants.constants import YES, NO, NOT_APPLICABLE

from ..form_validators import InfantFeedingFormValidator
from .models import ChildVisit, Appointment
from .test_model_mixin import TestModeMixin


@tag('inff')
class TestInfantFeedingFormValidator(TestModeMixin, TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(InfantFeedingFormValidator, *args, **kwargs)

    def setUp(self):

        appointment = Appointment.objects.create(
            subject_identifier='2334432',
            appt_datetime=timezone.now(),
            visit_code='2000',
            visit_instance='0')

        self.child_visit = ChildVisit.objects.create(
            subject_identifier='12345323',
            appointment=appointment)

        self.options = {
            'report_datetime': timezone.now(),
            'child_visit': self.child_visit,
            'ever_breastfed': NO,
            'freq_milk_rec': NOT_APPLICABLE,
            'rec_liquids': NO,
            'formula_water': 'blah blah',
            'taken_solid_foods': NO,
            'solid_foods': []
        }

    def test_form_valid(self):
        form_validator = InfantFeedingFormValidator(
            cleaned_data=self.options)
        try:
            form_validator.validate()
        except ValidationError as e:
            self.fail(f'ValidationError unexpectedly raised. Got{e}')

    def test_formula_took_invalid(self):

        self.options = {
            'report_datetime': timezone.now(),
            'child_visit': self.child_visit,
            'ever_breastfed': NO,
            'freq_milk_rec': NOT_APPLICABLE,
            'rec_liquids': NO,
            'formula_water': 'blah blah',
            'taken_solid_foods': NO,
            'solid_foods': [],
            'took_formula': YES
        }
        form_validator = InfantFeedingFormValidator(
            cleaned_data=self.options)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('dt_formula_introduced', form_validator._errors)

    def test_formula_took_invalid2(self):

        self.options = {
            'report_datetime': timezone.now(),
            'child_visit': self.child_visit,
            'ever_breastfed': NO,
            'freq_milk_rec': NOT_APPLICABLE,
            'rec_liquids': NO,
            'formula_water': 'blah blah',
            'taken_solid_foods': NO,
            'solid_foods': [],
            'took_formula': YES,
            'dt_formula_introduced': get_utcnow()
        }
        form_validator = InfantFeedingFormValidator(
            cleaned_data=self.options)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('dt_formula_est', form_validator._errors)

    #
    # def test_validate_apgar_1(self):
    #     self.options['apgar_score'] = YES
    #     form_validator = BirthDataFormValidator(
    #         cleaned_data=self.options)
    #     self.assertRaises(ValidationError, form_validator.validate)
    #     self.assertIn('apgar_score_min_1', form_validator._errors)
