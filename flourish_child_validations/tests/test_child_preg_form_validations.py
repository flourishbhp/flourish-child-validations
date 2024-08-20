from unittest.mock import Mock, patch

from dateutil.relativedelta import relativedelta
from django.core.exceptions import ValidationError
from django.test import tag, TestCase
from django.utils import timezone
from edc_base.utils import get_utcnow
from edc_constants.constants import NO, YES

from .models import Appointment, ChildVisit, RegisteredSubject
from .test_model_mixin import TestModelMixin
from ..form_validators import ChildPregTestingFormValidator


@tag('tpf')
class TestChildPregnacyFormValidator(TestModelMixin, TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(ChildPregTestingFormValidator, *args, **kwargs)

    def setUp(self):
        ChildPregTestingFormValidator.caregiver_child_consent_model = (
            'flourish_child_validations.caregiverchildconsent')
        ChildPregTestingFormValidator.child_preg_testing_model = (
            'flourish_child_validations.childpregtesting')
        ChildPregTestingFormValidator.tanner_staging_model = (
            'flourish_child_validations.childtannerstaging')
        appointment_1 = Appointment.objects.create(
            subject_identifier='2334432-1',
            appt_datetime=timezone.now(),
            visit_code='2000',
            visit_instance='0',
        )

        appointment_2 = Appointment.objects.create(
            subject_identifier='2334432-1',
            appt_datetime=timezone.now(),
            visit_code='2001',
            visit_instance='0',
        )

        child_visit = ChildVisit.objects.create(
            subject_identifier='2334432-1',
            appointment=appointment_1,
            schedule_name='child_a_quart_schedule1', )

        child_visit = ChildVisit.objects.create(
            subject_identifier='2334432-1',
            appointment=appointment_2,
            schedule_name='child_a_quart_schedule1', )

        RegisteredSubject.objects.create(
            subject_identifier=appointment_2.subject_identifier,
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
        self.options.update({'experienced_pregnancy': YES})
        self.options['last_menstrual_period'] = (
                    get_utcnow() - relativedelta(months=1)).date()
        self.options['menarche_start_dt'] = (
                    get_utcnow() - relativedelta(months=1)).date()

        self.options[field_name] = None

        form_validator = ChildPregTestingFormValidator(cleaned_data=self.options)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn(field_name, form_validator._errors)

    def test_lmp_date_estimated_invalid(self):
        self.options.update({'last_menstrual_period': None})
        self.options.update({'menarche': NO})

        form_validator = ChildPregTestingFormValidator(cleaned_data=self.options)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('is_lmp_date_estimated', form_validator._errors)

    def test_lmp_dt_against_today_dt_valid(self):

        self.options.update({'experienced_pregnancy': YES})
        self.options.update(
            {'last_menstrual_period': (get_utcnow() - relativedelta(months=1)).date()})
        self.options.update({'test_done': None})
        self.options.update({'test_date': None})
        self.options.update({'menarche_start_dt': 'blah'})
        self.options.update({'preg_test_result': None})

        form_validator = ChildPregTestingFormValidator(cleaned_data=self.options)
        try:
            form_validator.validate()
        except ValidationError as e:
            self.fail(f'ValidationError unexpectedly raised. Got{e}')

    def test_menarche_valid(self):

        self.options.update({'menarche': NO})
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


    def test_lmp_required_if_experienced_pregnancy(self):
        self.options.update({'menarche' : YES})
        self.options.update({'menarche_start_dt': 'blah'})
        self.options.update({'test_date': get_utcnow()})
        self.options.update({'last_menstrual_period': None})
        self.options.update({'is_lmp_date_estimated': None})
        form_validator = ChildPregTestingFormValidator(cleaned_data=self.options)
        try:
            form_validator.validate()
        except ValidationError as e:
            self.fail(f'ValidationError unexpectedly raised. Got{e}')

    @tag('xfail')
    def test_lmp_required_if_stated_menarche_and_not_first_start(self):
        self.options.update({'menarche' : YES})
        self.options.update({'menarche_start_dt': 'blah'})
        self.options.update({'test_date': get_utcnow()})
        self.options.update({'experienced_pregnancy': 'blah'})
        with patch.object(ChildPregTestingFormValidator, 'prev_objs',
                          new_callable=Mock) as mock_prev_objs:
            with patch.object(ChildPregTestingFormValidator, 'tanner_staging_objs',
                              new_callable=Mock) as mock_tanner_objs:
                mock_prev_objs.filter.return_value.exists.return_value = False
                mock_tanner_objs.exists.return_value = False

                form_validator = ChildPregTestingFormValidator(cleaned_data=self.options)
                self.assertRaises(ValidationError, form_validator.validate)
                self.assertIn('last_menstrual_period', form_validator._errors)


    def test_lmp_required_if_stated_menarche_and_tanner_staging_exists(self):
        self.options.update({'menarche' : YES})
        self.options.update({'menarche_start_dt': 'blah'})
        self.options.update({'test_date': get_utcnow()})
        with patch.object(ChildPregTestingFormValidator, 'prev_objs',
                          new_callable=Mock) as mock_prev_objs:
            with patch.object(ChildPregTestingFormValidator, 'tanner_staging_objs',
                              new_callable=Mock) as mock_tanner_objs:
                mock_prev_objs.filter.return_value.exists.return_value = False
                mock_tanner_objs.exists.return_value = True

                form_validator = ChildPregTestingFormValidator(cleaned_data=self.options)
                try:
                    form_validator.validate()
                except ValidationError as e:
                    self.fail(f'ValidationError unexpectedly raised. Got{e}')
