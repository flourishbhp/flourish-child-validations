from dateutil.relativedelta import relativedelta
from django.core.exceptions import ValidationError
from django.test import TestCase, tag
from django.utils import timezone
from edc_base.utils import get_utcnow
from edc_constants.constants import OTHER, YES, FEMALE

from ..form_validators import ChildClinicalMeasurementsFormValidator
from .models import ChildVisit, Appointment, CaregiverChildConsent, ChildAssent


@tag('cmf')
class TestClinicalMeasurementForm(TestCase):

    # def __init__(self, *args, **kwargs):
    #     super().__init__(ChildClinicalMeasurementsFormValidator, *args, **kwargs)

    def setUp(self):

        flourish_consent_version_model = 'flourish_child_validations.flourishconsentversion'
        subject_consent_model = 'flourish_child_validations.subjectconsent'
        child_caregiver_consent_model = 'flourish_child_validations.caregiverchildconsent'
        child_assent_model = 'flourish_child_validations.childassent'

        ChildClinicalMeasurementsFormValidator.consent_version_model = flourish_consent_version_model
        ChildClinicalMeasurementsFormValidator.subject_consent_model = subject_consent_model
        ChildClinicalMeasurementsFormValidator.maternal_delivery_model = subject_consent_model
        ChildClinicalMeasurementsFormValidator.child_assent_model = child_assent_model
        ChildClinicalMeasurementsFormValidator.child_caregiver_consent_model = child_caregiver_consent_model

        CaregiverChildConsent.objects.create(
            gender=FEMALE,
            consent_datetime=get_utcnow(),
            child_dob=get_utcnow() - relativedelta(years=6),
            subject_identifier='2334432')

        appointment = Appointment.objects.create(
            subject_identifier='2334432',
            appt_datetime=timezone.now(),
            visit_code='2000',
            visit_instance='0')

        self.child_visit = ChildVisit.objects.create(
            subject_identifier='2334432',
            appointment=appointment)

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
            subject_identifier='2334432',
            appt_datetime=timezone.now(),
            visit_code='3000',
            visit_instance='0')

        child_visit = ChildVisit.objects.create(
            subject_identifier='2334432',
            visit_code='3000',
            appointment=appointment)

        cleaned_data = {
            'child_visit': child_visit,
            'child_systolic_bp': 120,
            'child_diastolic_bp': 80,
            'skin_folds_triceps': None,
            'skin_folds_subscapular': None,
            'skin_folds_suprailiac': None
        }

        form_validator = ChildClinicalMeasurementsFormValidator(
            cleaned_data=cleaned_data)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('skin_folds_triceps', form_validator._errors)

    @tag('mwc')
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

    @tag('mwcr')
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
