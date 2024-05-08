from dateutil.relativedelta import relativedelta
from django.core.exceptions import ValidationError
from django.test import tag, TestCase
from django.utils import timezone
from edc_base.utils import get_utcnow
from edc_constants.constants import FEMALE, NO, YES

from .models import Appointment, CaregiverChildConsent, ChildVisit, RegisteredSubject
from .test_model_mixin import TestModelMixin
from ..form_validators import ChildClinicalMeasurementsFormValidator


@tag('cmf')
class TestClinicalMeasurementForm(TestModelMixin, TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(ChildClinicalMeasurementsFormValidator, *args, **kwargs)

    def setUp(self):
        CaregiverChildConsent.objects.create(
            gender=FEMALE,
            consent_datetime=get_utcnow(),
            child_dob=get_utcnow() - relativedelta(years=6),
            subject_identifier='2334432-10')

        appointment = Appointment.objects.create(
            subject_identifier='2334432-10',
            appt_datetime=timezone.now(),
            visit_code='2000',
            visit_instance='0')

        self.child_visit = ChildVisit.objects.create(
            subject_identifier=appointment.subject_identifier,
            appointment=appointment)

        RegisteredSubject.objects.create(
            subject_identifier=appointment.subject_identifier,
            relative_identifier='2334432', )

    def test_form_validation_for_child_under_1dot5_years(self):
        child_under_1dot5_years = CaregiverChildConsent.objects.create(
            gender=FEMALE,
            consent_datetime=get_utcnow(),
            child_dob=get_utcnow() - relativedelta(years=1, months=3), )

        appointment = Appointment.objects.create(
            subject_identifier=child_under_1dot5_years.subject_identifier,
            appt_datetime=timezone.now(),
            visit_code='2000',
            visit_instance='0')

        child_visit = ChildVisit.objects.create(
            subject_identifier=child_under_1dot5_years.subject_identifier,
            appointment=appointment)

        form_data = {'child_visit': child_visit,
                     'child_height': '75',
                     'child_weight_kg': '10'}
        form_validator = ChildClinicalMeasurementsFormValidator(
            cleaned_data=form_data)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('child_height', form_validator._errors)

    def test_form_validation_for_child_1dot5_years_old(self):
        child_1dot5_years = CaregiverChildConsent.objects.create(
            gender=FEMALE,
            consent_datetime=get_utcnow(),
            child_dob=get_utcnow() - relativedelta(years=2, months=3), )

        appointment = Appointment.objects.create(
            subject_identifier=child_1dot5_years.subject_identifier,
            appt_datetime=timezone.now(),
            visit_code='2000',
            visit_instance='0')

        child_visit = ChildVisit.objects.create(
            subject_identifier=child_1dot5_years.subject_identifier,
            appointment=appointment)

        form_data = {'child_visit': child_visit,
                     'child_height': '75',
                     'child_weight_kg': '10'}

        form_validator = ChildClinicalMeasurementsFormValidator(
            cleaned_data=form_data)
        try:
            form_validator.validate()
        except ValidationError as e:
            self.fail(f'ValidationError unexpectedly raised. Got{e}')

    def test_skin_folds_not_required_valid(self):
        cleaned_data = {
            'child_visit': self.child_visit,
            'child_systolic_bp': 120,
            'child_diastolic_bp': 80,
            'skin_folds_triceps': None,
            'skin_folds_subscapular': None,
            'skin_folds_suprailiac': None
        }

        form_validator = ChildClinicalMeasurementsFormValidator(
            cleaned_data=cleaned_data)
        try:
            form_validator.validate()
        except ValidationError as e:
            self.fail(f'ValidationError unexpectedly raised. Got{e}')

    @tag('cmf1')
    def test_skin_folds_not_required_invalid(self):

        appointment = Appointment.objects.create(
            subject_identifier='2334432-10',
            appt_datetime=timezone.now(),
            visit_code='3000',
            visit_instance='0')

        child_visit = ChildVisit.objects.create(
            subject_identifier='2334432-10',
            visit_code='3000',
            appointment=appointment)

        cleaned_data = {
            'child_visit': child_visit,
            'visit_skin_fold_messure': YES,
            'child_systolic_bp': 100,
            'child_diastolic_bp': 100,
            'skin_folds_triceps': None,
            'skin_folds_subscapular': None,
            'skin_folds_suprailiac': None
        }

        form_validator = ChildClinicalMeasurementsFormValidator(
            cleaned_data=cleaned_data)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('skin_folds_triceps', form_validator._errors)

    def test_measurement_validator_waist_circ_not_required(self):
        cleaned_data = {
            'child_visit': self.child_visit,
            'child_systolic_bp': 120,
            'child_waist_circ': 30.1,
            'child_waist_circ_second': 30,
            'child_waist_circ_third': 30.5,
            'child_diastolic_bp': 80,

        }

        form_validator = ChildClinicalMeasurementsFormValidator(
            cleaned_data=cleaned_data)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('child_waist_circ_third', form_validator._errors)

    def test_measurement_validator_waist_circ_required(self):
        cleaned_data = {
            'child_visit': self.child_visit,
            'child_systolic_bp': 120,
            'child_waist_circ': 30.1,
            'child_waist_circ_second': 33,
            'child_waist_circ_third': None,
            'child_diastolic_bp': 80,

        }

        form_validator = ChildClinicalMeasurementsFormValidator(
            cleaned_data=cleaned_data)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('child_waist_circ_third', form_validator._errors)

    def test_measurement_validator_child_hip_circ_required(self):
        cleaned_data = {
            'child_visit': self.child_visit,
            'child_systolic_bp': 120,
            'child_hip_circ': 30.1,
            'child_hip_circ_second': 34,
            'child_hip_circ_third': None,
            'child_diastolic_bp': 80,
        }
        form_validator = ChildClinicalMeasurementsFormValidator(
            cleaned_data=cleaned_data)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('child_hip_circ_third', form_validator._errors)

    def test_measurement_validator_child_hip_circ_not_required(self):
        cleaned_data = {
            'child_visit': self.child_visit,
            'child_systolic_bp': 120,
            'child_hip_circ': 30.1,
            'child_hip_circ_second': 30.2,
            'child_hip_circ_third': 30.4,
            'child_diastolic_bp': 80,
        }
        form_validator = ChildClinicalMeasurementsFormValidator(
            cleaned_data=cleaned_data)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('child_hip_circ_third', form_validator._errors)

    def test_skin_folds_measurement_required_when_visit_skin_fold_messure_is_yes(self):
        cleaned_data = {
            'child_visit': self.child_visit,
            'visit_skin_fold_messure': YES,
            'child_systolic_bp': 120,
            'skin_folds_triceps': None,
            'skin_folds_subscapular': None,
            'skin_folds_suprailiac': None,
            'child_diastolic_bp': 80,
        }

        form_validator = ChildClinicalMeasurementsFormValidator(
            cleaned_data=cleaned_data)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('skin_folds_triceps', form_validator._errors)

    def test_skin_folds_measurement_not_required_when_visit_skin_fold_messure_is_no(self):
        cleaned_data = {
            'child_visit': self.child_visit,
            'visit_skin_fold_messure': NO,
            'child_systolic_bp': 120,
            'skin_folds_triceps': None,
            'skin_folds_subscapular': None,
            'skin_folds_suprailiac': None,
            'child_diastolic_bp': 80,
        }

        form_validator = ChildClinicalMeasurementsFormValidator(
            cleaned_data=cleaned_data)
        try:
            form_validator.validate()
        except ValidationError as e:
            self.fail(f'ValidationError unexpectedly raised. Got{e}')

    def test_skin_folds_measurement_margin_of_error(self):
        cleaned_data = {
            'child_visit': self.child_visit,
            'child_systolic_bp': 120,
            'skin_folds_triceps': 5.4,
            'skin_folds_triceps_second': 6.4,
            'skin_folds_triceps_third': None,
            'skin_folds_subscapular': None,
            'skin_folds_suprailiac': None,
            'child_diastolic_bp': 80,
        }

        form_validator = ChildClinicalMeasurementsFormValidator(
            cleaned_data=cleaned_data)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('skin_folds_triceps_third', form_validator._errors)
