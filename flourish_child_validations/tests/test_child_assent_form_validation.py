from django.core.exceptions import ValidationError
from django.test import TestCase
from edc_base.utils import get_utcnow, relativedelta
from edc_constants.constants import YES, FEMALE, MALE, NOT_APPLICABLE

from ..form_validators import ChildAssentFormValidator
from .models import CaregiverConsent, ChildDataset, ScreeningPriorBhpParticipants
from .models import CaregiverChildConsent


class TestChildAssentForm(TestCase):

    def setUp(self):
        subject_consent_model = 'flourish_child_validations.caregiverconsent'
        ChildAssentFormValidator.subject_consent_model = subject_consent_model

        prior_screening_model = 'flourish_child_validations.screeningpriorbhpparticipants'
        ChildAssentFormValidator.prior_screening_model = prior_screening_model

        child_dataset_model = 'flourish_child_validations.childdataset'
        ChildAssentFormValidator.child_dataset_model = child_dataset_model

        child_assent_model = 'flourish_child_validations.childassent'
        ChildAssentFormValidator.child_assent_model = child_assent_model

        caregiver_child_consent_model = 'flourish_child_validations.caregiverchildconsent'
        ChildAssentFormValidator.caregiver_child_consent_model = caregiver_child_consent_model

        self.screening_identifier = 'ABC12345'
        self.study_child_identifier = '1234DCD'

        ScreeningPriorBhpParticipants.objects.create(
            screening_identifier=self.screening_identifier,
            report_datetime=get_utcnow(),
            study_child_identifier=self.study_child_identifier)

        self.subject_consent = CaregiverConsent.objects.create(
            subject_identifier='11111111',
            screening_identifier=self.screening_identifier,
            consent_datetime=get_utcnow() - relativedelta(years=2),
            dob=get_utcnow() - relativedelta(years=25),
            version='1')

        self.caregiver_child_consent = CaregiverChildConsent.objects.create(
            subject_identifier='11111111-10',
            consent_datetime=get_utcnow() - relativedelta(years=2),
            child_dob=(get_utcnow() - relativedelta(years=8)).date(),
            gender=FEMALE,
            identity='123425678',
            version='1',)

        self.child_assent_options = {
            'screening_identifier': self.screening_identifier,
            'subject_identifier': self.caregiver_child_consent.subject_identifier,
            'consent_datetime': get_utcnow(),
            'version': '1',
            'dob': (get_utcnow() - relativedelta(years=8)).date(),
            'gender': FEMALE,
            'first_name': 'TEST ONE',
            'last_name': 'TEST',
            'initials': 'TOT',
            'identity': '123425678',
            'identity_type': 'birth_cert',
            'confirm_identity': '123425678',
            'preg_testing': YES,
            'citizen': YES}

    def test_assent_dob_mismatch_consent_child_dob(self):
        self.caregiver_child_consent.child_dob = (get_utcnow() - relativedelta(years=9)).date()
        self.caregiver_child_consent.save_base(raw=True)
        form_validator = ChildAssentFormValidator(
            cleaned_data=self.child_assent_options)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('dob', form_validator._errors)

    def test_assent_dob_match_consent_child_dob(self):
        form_validator = ChildAssentFormValidator(
            cleaned_data=self.child_assent_options)
        try:
            form_validator.validate()
        except ValidationError as e:
            self.fail(f'ValidationError unexpectedly raised. Got{e}')

    def test_child_age_less_than_7years(self):
        self.caregiver_child_consent.child_dob = (get_utcnow() - relativedelta(years=6)).date()
        self.caregiver_child_consent.save_base(raw=True)
        self.child_assent_options.update(
            {'dob': (get_utcnow() - relativedelta(years=6)).date()})
        form_validator = ChildAssentFormValidator(
            cleaned_data=self.child_assent_options)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('dob', form_validator._errors)

    def test_child_gender_mismatch_dataset(self):
        self.caregiver_child_consent.gender = MALE
        self.caregiver_child_consent.save_base(raw=True)
        form_validator = ChildAssentFormValidator(
            cleaned_data=self.child_assent_options)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('gender', form_validator._errors)

    def test_child_gender_match_dataset(self):
        ChildDataset.objects.create(
            study_child_identifier=self.study_child_identifier,
            infant_sex='Female')
        form_validator = ChildAssentFormValidator(
            cleaned_data=self.child_assent_options)
        try:
            form_validator.validate()
        except ValidationError as e:
            self.fail(f'ValidationError unexpectedly raised. Got{e}')

    def test_preg_testing_for_female_invalid(self):
        self.child_assent_options.update({'preg_testing': NOT_APPLICABLE})
        form_validator = ChildAssentFormValidator(
            cleaned_data=self.child_assent_options)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('preg_testing', form_validator._errors)

    def test_preg_testing_test_female_valid(self):
        self.child_assent_options.update({'preg_testing': YES})

        form_validator = ChildAssentFormValidator(
            cleaned_data=self.child_assent_options)
        try:
            form_validator.validate()
        except ValidationError as e:
            self.fail(f'ValidationError unexpectedly raised. Got{e}')

    def test_preg_testing_for_male_invalid(self):
        self.caregiver_child_consent.gender = MALE
        self.caregiver_child_consent.identity = '123415678'
        self.caregiver_child_consent.save_base(raw=True)
        self.child_assent_options.update(
            {'gender': MALE,
             'preg_testing': YES,
             'identity': '123415678',
             'confirm_identity': '123415678'})
        form_validator = ChildAssentFormValidator(
            cleaned_data=self.child_assent_options)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('preg_testing', form_validator._errors)

    def test_identity_does_not_match(self):
        self.child_assent_options.update(
            {'preg_testing': YES,
             'confirm_identity': '123421678'})
        form_validator = ChildAssentFormValidator(
            cleaned_data=self.child_assent_options)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('identity', form_validator._errors)

    def test_first_name_last_name_valid(self):
        self.child_assent_options.update(
            {'first_name': 'TEST BONE',
             'last_name': 'TEST',
             'initials': 'TOT'})
        form_validator = ChildAssentFormValidator(
            cleaned_data=self.child_assent_options)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('initials', form_validator._errors)

    def test_first_name_last_name_invalid(self):
        self.child_assent_options.update(
            {'first_name': 'TEST ONE',
             'last_name': 'TEST',
             'initials': 'TOT'})
        form_validator = ChildAssentFormValidator(
            cleaned_data=self.child_assent_options)
        try:
            form_validator.validate()
        except ValidationError as e:
            self.fail(f'ValidationError unexpectedly raised. Got{e}')

    def test_first_name_invalid(self):
        self.child_assent_options.update(
            {'first_name': 'TEST ONE BEST',
             'last_name': 'TEST',
             'initials': 'TOT'})
        form_validator = ChildAssentFormValidator(
            cleaned_data=self.child_assent_options)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('first_name', form_validator._errors)
