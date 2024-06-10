from dateutil.relativedelta import relativedelta
from django.core.exceptions import ValidationError
from django.test import tag, TestCase
from django.utils import timezone
from edc_base import get_utcnow
from edc_constants.constants import FEMALE, NEG, NO, OTHER, PENDING, YES

from .models import Appointment, CaregiverChildConsent, ChildVisit, ListModel
from .test_model_mixin import TestModelMixin
from ..form_validators import InfantHIVTestingAdminFormValidatorRepeat, \
    InfantHIVTestingFormValidator


@tag('thit')
class TestHIVInfantTestingFormValidator(TestModelMixin, TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(InfantHIVTestingFormValidator, *args, **kwargs)

    def setUp(self):
        self.clean_data = {
            'child_tested_for_hiv': YES,
            'child_test_date': '2023-01-01',
            'child_test_date_estimated': NO,
            'results_received': YES,
            'recall_result_date': YES,
            'received_date': '2023-01-03',
            'result_date_estimated': NO,
            'hiv_test_result': NEG,
            'reason_child_not_tested': None,
            'reason_child_not_tested_other': None,
            'preferred_clinic_for_testing': None,
            'additional_comments': None,
            'test_visit': ListModel.objects.filter(
                short_name='6_'),
        }

        ListModel.objects.bulk_create(
            objs=[ListModel(short_name='birth', name='Birth'),
                  ListModel(short_name='6_to_8_weeks', name='6 to 8 weeks'),
                  ListModel(short_name='9_months', name='9-months'),
                  ListModel(short_name='18_months', name='18-months'),
                  ListModel(short_name=OTHER, name=OTHER),
                  ListModel(short_name='after_breastfeeding',
                            name='Three months after cessation of breastfeeding')])

        self.clean_data.update(test_visit=ListModel.objects.filter(
            short_name='after_breastfeeding'))

    def test_form_is_valid(self):
        form_validator = InfantHIVTestingFormValidator(
            cleaned_data=self.clean_data)
        try:
            form_validator.validate()
        except ValidationError as e:
            self.fail(f'ValidationError unexpectedly raised. Got{e}')

    def test_child_not_tested_reason_required(self):
        self.clean_data.update(
            child_tested_for_hiv=NO,
            child_test_date=None,
            received_date=None,
            results_received=None,
            recall_result_date=None,
            result_date_estimated=None,
            hiv_test_result=None,
            child_test_date_estimated=None,
            reason_child_not_tested=None)
        form_validator = InfantHIVTestingFormValidator(
            cleaned_data=self.clean_data)
        self.clean_data.pop('test_visit')
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('reason_child_not_tested', form_validator._errors)

    def test_reason_child_not_tested_other_required(self):
        self.clean_data.update(
            child_tested_for_hiv=NO,
            reason_child_not_tested=ListModel.objects.filter(
                short_name=OTHER),
            child_test_date=None,
            received_date=None,
            results_received=None,
            recall_result_date=None,
            result_date_estimated=None,
            hiv_test_result=None,
            child_test_date_estimated=None,
            reason_child_not_tested_other=None,
        )
        self.clean_data.pop('test_visit')
        form_validator = InfantHIVTestingFormValidator(
            cleaned_data=self.clean_data)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('reason_child_not_tested_other', form_validator._errors)

    def test_hiv_test_result_before_test_date_invalid(self):
        self.clean_data.update(
            results_received=NO,
            child_test_date='2022-11-19',
            received_date='2022-11-18',
            test_visit=ListModel.objects.filter(
                short_name='after_breastfeeding'),
        )
        form_validator = InfantHIVTestingAdminFormValidatorRepeat(
            cleaned_data=self.clean_data)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('received_date', form_validator._errors)

    def test_reason_child_not_tested_other_not_required(self):
        self.clean_data.update(
            reason_child_not_tested=None,
            reason_child_not_tested_other='blah',
            test_visit=ListModel.objects.filter(
                short_name='after_breastfeeding'),
        )
        form_validator = InfantHIVTestingFormValidator(
            cleaned_data=self.clean_data)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('reason_child_not_tested_other', form_validator._errors)

    def test_validate_age_less_than_6_weeks(self):
        child_under_1dot5_years = CaregiverChildConsent.objects.create(
            gender=FEMALE,
            consent_datetime=get_utcnow(),
            child_dob=get_utcnow() - relativedelta(years=0, months=1), )

        appointment = Appointment.objects.create(
            subject_identifier=child_under_1dot5_years.subject_identifier,
            appt_datetime=timezone.now(),
            visit_code='2000',
            visit_instance='0')

        child_visit = ChildVisit.objects.create(
            subject_identifier=child_under_1dot5_years.subject_identifier,
            appointment=appointment)

        form_data = {'child_visit': child_visit,
                     'test_visit': ListModel.objects.filter(
                         short_name='6_to_8_weeks')}

        form_validator = InfantHIVTestingFormValidator(
            cleaned_data=form_data)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('test_visit', form_validator._errors)

    def test_validate_age_less_than_9_months(self):
        child_under_1dot5_years = CaregiverChildConsent.objects.create(
            gender=FEMALE,
            consent_datetime=get_utcnow(),
            child_dob=get_utcnow() - relativedelta(years=0, months=6), )

        appointment = Appointment.objects.create(
            subject_identifier=child_under_1dot5_years.subject_identifier,
            appt_datetime=timezone.now(),
            visit_code='2000',
            visit_instance='0')

        child_visit = ChildVisit.objects.create(
            subject_identifier=child_under_1dot5_years.subject_identifier,
            appointment=appointment)

        form_data = {'child_visit': child_visit,
                     'test_visit': ListModel.objects.filter(
                         short_name='9_months')}

        form_validator = InfantHIVTestingFormValidator(
            cleaned_data=form_data)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('test_visit', form_validator._errors)

    def test_validate_age_less_than_18_months(self):
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
                     'test_visit': ListModel.objects.filter(
                         short_name='18_months')}

        form_validator = InfantHIVTestingFormValidator(
            cleaned_data=form_data)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('test_visit', form_validator._errors)

    def test_validate_results_pending(self):
        form_data = {
            'results_received': YES,
            'received_date': get_utcnow(),
            'result_date_estimated': NO,
            'hiv_test_result': PENDING
        }
        form = InfantHIVTestingAdminFormValidatorRepeat(form_data)

        with self.assertRaises(ValidationError) as cm:
            form.clean()

        self.assertIn('hiv_test_result', str(cm.exception))
