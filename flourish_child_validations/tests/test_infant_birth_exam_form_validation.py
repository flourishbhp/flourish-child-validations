# from dateutil.relativedelta import relativedelta
# from django.core.exceptions import ValidationError
# from django.test import TestCase
# from edc_base.utils import get_utcnow
# from edc_constants.constants import ABNORMAL, NORMAL, YES, NO
#
# from ..form_validators import BirthExamFormValidator
# from .models import RegisteredSubject, CaregiverConsent, Appointment, ChildVisit
#
#
# class TestBirthExamFormValidator(TestCase):
#
#     def setUp(self):
#         subject_identifier = '22334'
#         relative_identifier = '12334'
#         appointment = Appointment.objects.create(
#             subject_identifier=subject_identifier,
#             appt_datetime=get_utcnow(),
#             visit_code='2000')
#         self.infant_visit = ChildVisit.objects.create(
#             subject_identifier=appointment.subject_identifier,
#             appointment=appointment,
#             report_datetime=get_utcnow())
#         RegisteredSubject.objects.create(
#             subject_identifier=subject_identifier,
#             relative_identifier=relative_identifier)
#         registered_subject_model = 'flourish_child_validations.registeredsubject'
#         BirthExamFormValidator.registered_subject_model =\
#             registered_subject_model
#         self.maternal_consent = CaregiverConsent.objects.create(
#             subject_identifier=relative_identifier,
#             consent_datetime=get_utcnow() - relativedelta(days=10),
#             dob=(get_utcnow() - relativedelta(years=23)).date())
#         maternal_consent_model = 'flourish_child_validations.caregiverconsent'
#         BirthExamFormValidator.maternal_consent_model =\
#             maternal_consent_model
#
#     def test_report_datetime_before_visit_datetime_invalid(self):
#         cleaned_data = {
#             'infant_visit': self.infant_visit,
#             'report_datetime': get_utcnow() - relativedelta(days=11)}
#         form_validator = BirthExamFormValidator(
#             cleaned_data=cleaned_data)
#         self.assertRaises(ValidationError, form_validator.validate)
#
#     def test_report_datetime_after_visit_datetime_valid(self):
#         cleaned_data = {
#             'infant_visit': self.infant_visit,
#             'report_datetime': get_utcnow()
#         }
#         form_validator = BirthExamFormValidator(
#             cleaned_data=cleaned_data)
#         try:
#             form_validator.validate()
#         except ValidationError as e:
#             self.fail(f'ValidationError unexpectedly raised. Got{e}')
#
#     def test_general_activity_abnormal_not_specified(self):
#         cleaned_data = {
#             'infant_visit': self.infant_visit,
#             'report_datetime': get_utcnow(),
#             'general_activity': ABNORMAL,
#             'abnormal_activity': None
#         }
#         form_validator = BirthExamFormValidator(
#             cleaned_data=cleaned_data)
#         self.assertRaises(ValidationError, form_validator.validate)
#         self.assertIn('abnormal_activity', form_validator._errors)
#
#     def test_general_activity_abnormal_specified(self):
#         cleaned_data = {
#             'infant_visit': self.infant_visit,
#             'report_datetime': get_utcnow(),
#             'general_activity': ABNORMAL,
#             'abnormal_activity': 'blah blah blah'
#         }
#         form_validator = BirthExamFormValidator(
#             cleaned_data=cleaned_data)
#         try:
#             form_validator.validate()
#         except ValidationError as e:
#             self.fail(f'ValidationError unexpectedly raised. Got{e}')
#
#     def test_general_activity_normal_abn_activity_invalid(self):
#         cleaned_data = {
#             'infant_visit': self.infant_visit,
#             'report_datetime': get_utcnow(),
#             'general_activity': NORMAL,
#             'abnormal_activity': 'Some creepy stuff'
#         }
#         form_validator = BirthExamFormValidator(
#             cleaned_data=cleaned_data)
#         self.assertRaises(ValidationError, form_validator.validate)
#         self.assertIn('abnormal_activity', form_validator._errors)
#
#     def test_general_activity_normal_abn_activity_none_valid(self):
#         cleaned_data = {
#             'infant_visit': self.infant_visit,
#             'report_datetime': get_utcnow(),
#             'general_activity': NORMAL,
#             'abnormal_activity': None
#         }
#         form_validator = BirthExamFormValidator(
#             cleaned_data=cleaned_data)
#         try:
#             form_validator.validate()
#         except ValidationError as e:
#             self.fail(f'ValidationError unexpectedly raised. Got{e}')
#
#     def test_heent_exam_yes_heent_no_other_invalid(self):
#         cleaned_data = {
#             'infant_visit': self.infant_visit,
#             'report_datetime': get_utcnow(),
#             'general_activity': NORMAL,
#             'abnormal_activity': None,
#             'heent_exam': YES,
#             'heent_no_other': 'specified'}
#         form_validator = BirthExamFormValidator(
#             cleaned_data=cleaned_data)
#         self.assertRaises(ValidationError, form_validator.validate)
#         self.assertIn('heent_no_other', form_validator._errors)
#
#     def test_heent_exam_yes_heent_no_other_none_valid(self):
#         cleaned_data = {
#             'infant_visit': self.infant_visit,
#             'report_datetime': get_utcnow(),
#             'general_activity': NORMAL,
#             'abnormal_activity': None,
#             'heent_exam': YES,
#             'heent_no_other': None}
#         form_validator = BirthExamFormValidator(
#             cleaned_data=cleaned_data)
#         try:
#             form_validator.validate()
#         except ValidationError as e:
#             self.fail(f'ValidationError unexpectedly raised. Got{e}')
#
#     def test_heent_exam_no_heent_no_other_required(self):
#         cleaned_data = {
#             'infant_visit': self.infant_visit,
#             'report_datetime': get_utcnow(),
#             'general_activity': NORMAL,
#             'abnormal_activity': None,
#             'heent_exam': NO,
#             'heent_no_other': None}
#         form_validator = BirthExamFormValidator(
#             cleaned_data=cleaned_data)
#         self.assertRaises(ValidationError, form_validator.validate)
#         self.assertIn('heent_no_other', form_validator._errors)
#
#     def test_heent_exam_no_heent_no_other_specified(self):
#         cleaned_data = {
#             'infant_visit': self.infant_visit,
#             'report_datetime': get_utcnow(),
#             'general_activity': NORMAL,
#             'abnormal_activity': None,
#             'heent_exam': NO,
#             'heent_no_other': 'specified'}
#         form_validator = BirthExamFormValidator(
#             cleaned_data=cleaned_data)
#         try:
#             form_validator.validate()
#         except ValidationError as e:
#             self.fail(f'ValidationError unexpectedly raised. Got{e}')
#
#     def test_resp_exam_yes_resp_exam_other_invalid(self):
#         cleaned_data = {
#             'infant_visit': self.infant_visit,
#             'report_datetime': get_utcnow(),
#             'general_activity': NORMAL,
#             'abnormal_activity': None,
#             'resp_exam': YES,
#             'resp_exam_other': 'specified'}
#         form_validator = BirthExamFormValidator(
#             cleaned_data=cleaned_data)
#         self.assertRaises(ValidationError, form_validator.validate)
#         self.assertIn('resp_exam_other', form_validator._errors)
#
#     def test_resp_exam_yes_resp_exam_other_none_valid(self):
#         cleaned_data = {
#             'infant_visit': self.infant_visit,
#             'report_datetime': get_utcnow(),
#             'general_activity': NORMAL,
#             'abnormal_activity': None,
#             'resp_exam': YES,
#             'resp_exam_other': None}
#         form_validator = BirthExamFormValidator(
#             cleaned_data=cleaned_data)
#         try:
#             form_validator.validate()
#         except ValidationError as e:
#             self.fail(f'ValidationError unexpectedly raised. Got{e}')
#
#     def test_resp_exam_no_resp_exam_other_required(self):
#         cleaned_data = {
#             'infant_visit': self.infant_visit,
#             'report_datetime': get_utcnow(),
#             'general_activity': NORMAL,
#             'abnormal_activity': None,
#             'resp_exam': NO,
#             'resp_exam_other': None}
#         form_validator = BirthExamFormValidator(
#             cleaned_data=cleaned_data)
#         self.assertRaises(ValidationError, form_validator.validate)
#         self.assertIn('resp_exam_other', form_validator._errors)
#
#     def test_resp_exam_no_resp_exam_other_specified(self):
#         cleaned_data = {
#             'infant_visit': self.infant_visit,
#             'report_datetime': get_utcnow(),
#             'general_activity': NORMAL,
#             'abnormal_activity': None,
#             'resp_exam': NO,
#             'resp_exam_other': 'specified'}
#         form_validator = BirthExamFormValidator(
#             cleaned_data=cleaned_data)
#         try:
#             form_validator.validate()
#         except ValidationError as e:
#             self.fail(f'ValidationError unexpectedly raised. Got{e}')
#
#     def test_cardiac_exam_yes_cardiac_exam_other_invalid(self):
#         cleaned_data = {
#             'infant_visit': self.infant_visit,
#             'report_datetime': get_utcnow(),
#             'general_activity': NORMAL,
#             'abnormal_activity': None,
#             'cardiac_exam': YES,
#             'cardiac_exam_other': 'specified'}
#         form_validator = BirthExamFormValidator(
#             cleaned_data=cleaned_data)
#         self.assertRaises(ValidationError, form_validator.validate)
#         self.assertIn('cardiac_exam_other', form_validator._errors)
#
#     def test_cardiac_exam_yes_cardiac_exam_other_none_valid(self):
#         cleaned_data = {
#             'infant_visit': self.infant_visit,
#             'report_datetime': get_utcnow(),
#             'general_activity': NORMAL,
#             'abnormal_activity': None,
#             'cardiac_exam': YES,
#             'cardiac_exam_other': None}
#         form_validator = BirthExamFormValidator(
#             cleaned_data=cleaned_data)
#         try:
#             form_validator.validate()
#         except ValidationError as e:
#             self.fail(f'ValidationError unexpectedly raised. Got{e}')
#
#     def test_cardiac_exam_no_cardiac_exam_other_required(self):
#         cleaned_data = {
#             'infant_visit': self.infant_visit,
#             'report_datetime': get_utcnow(),
#             'general_activity': NORMAL,
#             'abnormal_activity': None,
#             'cardiac_exam': NO,
#             'cardiac_exam_other': None}
#         form_validator = BirthExamFormValidator(
#             cleaned_data=cleaned_data)
#         self.assertRaises(ValidationError, form_validator.validate)
#         self.assertIn('cardiac_exam_other', form_validator._errors)
#
#     def test_cardiac_exam_no_cardiac_exam_other_specified(self):
#         cleaned_data = {
#             'infant_visit': self.infant_visit,
#             'report_datetime': get_utcnow(),
#             'general_activity': NORMAL,
#             'abnormal_activity': None,
#             'cardiac_exam': NO,
#             'cardiac_exam_other': 'specified'}
#         form_validator = BirthExamFormValidator(
#             cleaned_data=cleaned_data)
#         try:
#             form_validator.validate()
#         except ValidationError as e:
#             self.fail(f'ValidationError unexpectedly raised. Got{e}')
