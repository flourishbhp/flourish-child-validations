from django.apps import apps as django_apps
from django.core.exceptions import ValidationError
from django.test import TestCase
from edc_base.utils import get_utcnow
from edc_constants.constants import YES, NO

from ..form_validators import ChildSocioDemographicFormValidator
from .models import (Appointment, OnSchedule, CaregiverSocioDemographicData,
                     RegisteredSubject, ChildVisit as Visit)
from .test_model_mixin import TestModelMixin


def onschedule_model_cls(self, onschedule_model):
    return OnSchedule or django_apps.get_model(onschedule_model)


class TestSocioDemographicFormValidations(TestModelMixin, TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(ChildSocioDemographicFormValidator, *args, **kwargs)

    def setUp(self):
        ChildSocioDemographicFormValidator.onschedule_model_cls = onschedule_model_cls
        self.caregiver_subject_identifier = '123456789'
        child_1_subject_identifier = f'{self.caregiver_subject_identifier}-1'
        child_2_subject_identifier = f'{self.caregiver_subject_identifier}-2'

        RegisteredSubject.objects.create(
            subject_identifier=child_1_subject_identifier,
            relative_identifier=self.caregiver_subject_identifier, )

        RegisteredSubject.objects.create(
            subject_identifier=child_2_subject_identifier,
            relative_identifier=self.caregiver_subject_identifier, )

        OnSchedule.objects.create(
            subject_identifier=self.caregiver_subject_identifier,
            child_subject_identifier=child_1_subject_identifier,
            schedule_name='cohort_a_enrollment', )

        OnSchedule.objects.create(
            subject_identifier=self.caregiver_subject_identifier,
            child_subject_identifier=child_2_subject_identifier,
            schedule_name='cohort_b_enrollment', )

        child_appointment_1 = Appointment.objects.create(
            subject_identifier=child_1_subject_identifier,
            appt_datetime=get_utcnow(),
            visit_code='2000',
            visit_instance='0')

        self.child_visit_1 = Visit.objects.create(
            appointment=child_appointment_1,
            visit_code_sequence='0',
            schedule_name='child_cohort_a_enrolment',
            visit_code=child_appointment_1.visit_code, )

        caregiver_appointment_1 = Appointment.objects.create(
            subject_identifier=self.caregiver_subject_identifier,
            appt_datetime=get_utcnow(),
            visit_code='2000M',
            visit_instance='0')

        caregiver_visit_1 = Visit.objects.create(
            appointment=caregiver_appointment_1,
            subject_identifier=self.caregiver_subject_identifier,
            schedule_name='cohort_a_enrollment',
            visit_code_sequence='0',
            visit_code=caregiver_appointment_1.visit_code)

        caregiver_appointment_2 = Appointment.objects.create(
            subject_identifier=self.caregiver_subject_identifier,
            appt_datetime=get_utcnow(),
            visit_code='2000M',
            visit_instance='0')

        caregiver_visit_2 = Visit.objects.create(
            appointment=caregiver_appointment_2,
            subject_identifier=self.caregiver_subject_identifier,
            schedule_name='cohort_b_enrollment',
            visit_code_sequence='0',
            visit_code=caregiver_appointment_2.visit_code, )

        CaregiverSocioDemographicData.objects.create(
            maternal_visit=caregiver_visit_1,
            stay_with_child=YES)

        CaregiverSocioDemographicData.objects.create(
            maternal_visit=caregiver_visit_2,
            stay_with_child=NO)

    def test_validate_child_stay_with_caregiver(self):
        cleaned_data = {
            'child_visit': self.child_visit_1,
            'stay_with_caregiver': YES
        }
        form_validator = ChildSocioDemographicFormValidator(
            cleaned_data=cleaned_data)
        try:
            form_validator.validate()
        except ValidationError as e:
            self.fail(f'ValidationError unexpectedly raised. Got{e}')

    def test_validate_child_does_not_stay_with_caregiver(self):
        cleaned_data = {
            'child_visit': self.child_visit_1,
            'stay_with_caregiver': NO
        }
        form_validator = ChildSocioDemographicFormValidator(
            cleaned_data=cleaned_data)
        self.assertRaises(ValidationError, form_validator.validate)
