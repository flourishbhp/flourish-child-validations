from django.apps import apps as django_apps
from django.core.exceptions import ValidationError
from django.test import TestCase, tag
from edc_base.utils import get_utcnow
from edc_constants.constants import YES, NO

from flourish_child_validations.form_validators import ChildSocioDemographicFormValidator
from flourish_child_validations.tests.models import Appointment, ChildVisit as Visit, \
    Schedule, OnSchedule


# @tag('socio')
class TestSocioDemographicFormValidations(TestCase):

    def __init__(self, methodName: str = ...):
        super().__init__(methodName)
        self.child_visit_1 = None
        self.caregiver_subject_identifier = None

    def setUp(self):
        flourish_consent_version_model = 'flourish_child_validations.flourishconsentversion'
        subject_consent_model = 'flourish_child_validations.subjectconsent'
        child_caregiver_consent_model = 'flourish_child_validations.caregiverchildconsent'
        child_assent_model_model = 'flourish_child_validations.childassent'
        caregiver_socio_demographic_model = \
            'flourish_child_validations.caregiversociodemographicdata'
        maternal_delivery_model = 'flourish_child_validations.maternaldelivery'

        ChildSocioDemographicFormValidator.consent_version_model = flourish_consent_version_model
        ChildSocioDemographicFormValidator.child_assent_model = child_assent_model_model
        ChildSocioDemographicFormValidator.subject_consent_model = subject_consent_model
        ChildSocioDemographicFormValidator.child_caregiver_consent_model = child_caregiver_consent_model
        ChildSocioDemographicFormValidator.caregiver_socio_demographic_model = caregiver_socio_demographic_model
        ChildSocioDemographicFormValidator.maternal_delivery_model = maternal_delivery_model

        self.caregiver_subject_identifier = '123456789'
        child_1_subject_identifier = f'{self.caregiver_subject_identifier}-1'
        child_2_subject_identifier = f'{self.caregiver_subject_identifier}-2'
        caregiver_socio_demographic_cls = django_apps.get_model(
            caregiver_socio_demographic_model)

        OnSchedule.objects.create(
            subject_identifier=self.caregiver_subject_identifier,

            child_subject_identifier=child_1_subject_identifier,

            schedule_name='CohortAQuarterly'
        )

        OnSchedule.objects.create(
            subject_identifier=self.caregiver_subject_identifier,

            child_subject_identifier=child_2_subject_identifier,

            schedule_name='CohortBEnrollment'
        )

        child_onschedule_a_obj = Schedule.objects.create(
            schedule_name='CohortAQuarterly',
            subject_identifier=self.caregiver_subject_identifier,
            child_subject_identifier=child_1_subject_identifier,
            onschedule_model='flourish_child_validations.onschedule'
        )

        caregiver_onschedule_a_obj = Schedule.objects.create(
            schedule_name='CohortAQuarterly',
            subject_identifier=self.caregiver_subject_identifier,
            child_subject_identifier=child_1_subject_identifier,
            onschedule_model='flourish_child_validations.onschedule'
        )

        caregiver_onschedule_b_obj = Schedule.objects.create(
            schedule_name='CohortBEnrollment',
            subject_identifier=self.caregiver_subject_identifier,
            child_subject_identifier=child_2_subject_identifier,
            onschedule_model='flourish_child_validations.onschedule'
        )

        child_appointment_1 = Appointment.objects.create(
            subject_identifier=child_1_subject_identifier,
            appt_datetime=get_utcnow(),
            visit_code='2000',
            visit_instance='0')

        self.child_visit_1 = Visit.objects.create(
            subject_identifier=child_1_subject_identifier,
            visit_code_sequence='0',
            schedule=child_onschedule_a_obj,
            visit_code=child_appointment_1.visit_code,
            appointment=child_appointment_1)

        caregiver_appointment_1 = Appointment.objects.create(
            subject_identifier=caregiver_onschedule_a_obj.subject_identifier,
            appt_datetime=get_utcnow(),
            visit_code='2000M',
            visit_instance='0')

        caregiver_visit_1 = Visit.objects.create(
            subject_identifier=caregiver_onschedule_a_obj.subject_identifier,
            schedule_name=caregiver_onschedule_a_obj.schedule_name,
            schedule=caregiver_onschedule_a_obj,
            visit_code_sequence='0',
            visit_code=caregiver_appointment_1.visit_code,
            appointment=caregiver_appointment_1)

        caregiver_appointment_2 = Appointment.objects.create(
            subject_identifier=caregiver_onschedule_b_obj.subject_identifier,
            appt_datetime=get_utcnow(),
            visit_code='2000M',
            visit_instance='0')

        caregiver_visit_2 = Visit.objects.create(
            subject_identifier=caregiver_onschedule_b_obj.subject_identifier,
            schedule_name=caregiver_onschedule_b_obj.schedule_name,
            schedule=caregiver_onschedule_b_obj,
            visit_code_sequence='0',
            visit_code=caregiver_appointment_2.visit_code,
            appointment=caregiver_appointment_2)

        caregiver_socio_demographic_cls.objects.create(
            maternal_visit=caregiver_visit_1,
            stay_with_child=YES
        )

        caregiver_socio_demographic_cls.objects.create(
            maternal_visit=caregiver_visit_2,
            stay_with_child=NO
        )

    @tag('socio')
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

    @tag('socio')
    def test_validate_child_does_not_stay_with_caregiver(self):
        cleaned_data = {
            'child_visit': self.child_visit_1,
            'stay_with_caregiver': NO
        }
        form_validator = ChildSocioDemographicFormValidator(
            cleaned_data=cleaned_data)
        self.assertRaises(ValidationError, form_validator.validate)
