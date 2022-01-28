from dateutil.relativedelta import relativedelta
from django.core.exceptions import ValidationError
from django.test import TestCase, tag
from edc_base.utils import get_utcnow
from edc_constants.constants import FEMALE

from ..form_validators import ChildVisitFormValidator
from .models import CaregiverChildConsent
from .models import CaregiverConsent, Appointment, ScreeningPriorBhpParticipants


@tag('iv')
class TestChildVisitFormValidator(TestCase):
    pass

    # def setUp(self):
    #
        # caregiver_child_consent_model = 'flourish_child_validations.caregiverchildconsent'
        # ChildVisitFormValidator.caregiver_child_consent_model = caregiver_child_consent_model
        #
        # ScreeningPriorBhpParticipants.objects.create(
            # screening_identifier='S99112',
            # report_datetime=get_utcnow(),
            # study_child_identifier=self.study_child_identifier)
            #
        # self.subject_consent = CaregiverConsent.objects.create(
            # subject_identifier='11111111',
            # screening_identifier='S99112',
            # consent_datetime=get_utcnow() - relativedelta(years=2),
            # dob=get_utcnow() - relativedelta(years=25),
            # version='1')
            #
        # self.caregiver_child_consent = CaregiverChildConsent.objects.create(
            # subject_identifier='11111111-10',
            # consent_datetime=get_utcnow() - relativedelta(years=2),
            # child_dob=(get_utcnow() - relativedelta(years=5)).date(),
            # gender=FEMALE,
            # identity='123425678',
            # version='1',)
            #
        # self.appointment = Appointment.objects.create(
            # subject_identifier=self.subject_identifier,
            # appt_datetime=get_utcnow(),
            # visit_code='2000')
            #
    # def test_current_consent_version_exists(self):
        # cleaned_data = {
            # 'appointment': self.appointment,
            # 'subject_identifier': self.subject_identifier}
        # form_validator = ChildVisitFormValidator(cleaned_data=cleaned_data)
        # try:
            # form_validator.validate()
        # except ValidationError as e:
            # self.fail(f'ValidationError unexpectedly raised. Got{e}')
