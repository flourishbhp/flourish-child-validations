from django.core.exceptions import ValidationError
from django.test import tag, TestCase
from django.utils import timezone
from edc_base.utils import get_utcnow
from edc_constants.constants import NO, NOT_APPLICABLE, YES

from .models import Appointment, ChildBirth, ChildVisit, ListModel, RegisteredSubject
from .test_model_mixin import TestModelMixin
from ..form_validators import InfantFeedingFormValidator


@tag('inff')
class TestInfantFeedingFormValidator(TestModelMixin, TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(InfantFeedingFormValidator, *args, **kwargs)

    def setUp(self):
        appointment = Appointment.objects.create(
            subject_identifier='2334432-1',
            appt_datetime=get_utcnow(),
            visit_code='2000',
            visit_instance='0')

        self.child_visit = ChildVisit.objects.create(
            appointment=appointment,
            report_datetime=get_utcnow())

        RegisteredSubject.objects.create(
            subject_identifier=appointment.subject_identifier,
            relative_identifier='2334432', )

        ChildBirth.objects.create(
            subject_identifier=appointment.subject_identifier,
            dob=get_utcnow(),
            report_datetime=get_utcnow())

        self.subject_identifier = appointment.subject_identifier

        self.options = {
            'report_datetime': timezone.now(),
            'child_visit': self.child_visit,
            'ever_breastfed': NO,
            'freq_milk_rec': NOT_APPLICABLE,
            'rec_liquids': NO,
            'formula_water': 'blah blah',
            'taken_solid_foods': NO,
            'solid_foods': ListModel.objects.filter(
                short_name='xx'),
            'solid_foods_past_week': ListModel.objects.filter(
                short_name='xx')
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
            'rec_liquids': YES,
            'formula_water': 'blah blah',
            'taken_solid_foods': NO,
            'solid_foods': [],
            'took_formula': YES,
            'dt_formula_introduced': None
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
            'rec_liquids': YES,
            'formula_water': 'blah blah',
            'taken_solid_foods': NO,
            'solid_foods': [],
            'took_formula': YES,
            'dt_formula_introduced': get_utcnow().date()
        }
        form_validator = InfantFeedingFormValidator(
            cleaned_data=self.options)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('dt_formula_est', form_validator._errors)
