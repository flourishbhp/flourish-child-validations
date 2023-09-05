from dateutil.relativedelta import relativedelta
from django.core.exceptions import ValidationError
from django.test import TestCase, tag
from django.utils import timezone
from edc_base.utils import get_utcnow
from edc_constants.constants import NO, YES

from ..form_validators import ChildPregTestingFormValidator

from .test_model_mixin import TestModelMixin
from .models import ChildVisit, Appointment, RegisteredSubject


@tag('tpf')
class TestChildPregnacyFormValidator(TestModelMixin, TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(ChildPregTestingFormValidator, *args, **kwargs)

    def setUp(self):
        appointment = Appointment.objects.create(
            subject_identifier='2334432-1',
            appt_datetime=timezone.now(),
            visit_code='2001',
            visit_instance='0',
           )

        child_visit = ChildVisit.objects.create(
            subject_identifier='2334432-1',
            appointment=appointment,
            schedule_name='child_a_quart_schedule1',)

        RegisteredSubject.objects.create(
            subject_identifier=appointment.subject_identifier,
            relative_identifier='2334432', )

        self.options = {
            'test_done': YES,
            'last_menstrual_period': get_utcnow(),
            'is_lmp_date_estimated': NO,
            'preg_test_result': 'Negative',
            'child_visit': child_visit,
            'menarche': YES,
            }

    def test_pregnancy_test_required_v_2000_valid(self):
        appointment2 = Appointment.objects.create(
            subject_identifier='2334432',
            appt_datetime=timezone.now(),
            visit_code='2000',
            visit_instance='0',
           )

        visit = ChildVisit.objects.create(
            subject_identifier='12345323',
            appointment=appointment2,
            schedule_name='child_c_enrol_schedule1',
            visit_code='2000',
            )

        self.data = {
            'test_done': YES,
            'preg_test_result': 'Negative',
            'child_visit': visit,
            'test_date': (get_utcnow() - relativedelta(months=1)).date()
            }

        form_validator = ChildPregTestingFormValidator(cleaned_data=self.data)
        try:
            form_validator.validate()
        except ValidationError as e:
            self.fail(f'ValidationError unexpectedly raised. Got{e}')

    def test_lmp_date_estimated_required(self):

        field_name = 'is_lmp_date_estimated'
        self.options['last_menstrual_period'] = (get_utcnow() - relativedelta(months=1)).date()

        self.options[field_name] = None

        form_validator = ChildPregTestingFormValidator(cleaned_data=self.options)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn(field_name, form_validator._errors)

    def test_lmp_date_estimated_invalid(self):
        self.options.update({'last_menstrual_period': None})
        self.options.update({'menarche':NO})

        form_validator = ChildPregTestingFormValidator(cleaned_data=self.options)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('is_lmp_date_estimated', form_validator._errors)

    def test_lmp_dt_against_today_dt_valid(self):

        self.options.update({'last_menstrual_period': (get_utcnow() - relativedelta(months=1)).date() })
        self.options.update({'test_done': None})
        self.options.update({'test_date': None})
        self.options.update({'preg_test_result': None})

        form_validator = ChildPregTestingFormValidator(cleaned_data=self.options)
        try:
            form_validator.validate()
        except ValidationError as e:
            self.fail(f'ValidationError unexpectedly raised. Got{e}')

    def test_menarche_valid(self):

        self.options.update({'menarche':NO})
        self.options.update({'last_menstrual_period': None})
        self.options.update({'is_lmp_date_estimated': None})
        self.options.update({'test_done': None})
        self.options.update({'test_date': None})
        self.options.update({'preg_test_result': None})

        form_validator = ChildPregTestingFormValidator(cleaned_data=self.options)
        try:
            form_validator.validate()
        except ValidationError as e:
            self.fail(f'ValidationError unexpectedly raised. Got{e}')

