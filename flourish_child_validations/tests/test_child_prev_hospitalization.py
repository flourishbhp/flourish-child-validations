from django.core.exceptions import ValidationError
from django.test import TestCase, tag
from edc_base.utils import get_utcnow
from edc_constants.constants import OTHER, YES

from .models import Appointment, ChildVisit, ListModel, RegisteredSubject
from .test_model_mixin import TestModelMixin
from ..form_validators import (ChildPreHospitalisationInlineFormValidator, 
                               ChildPreviousHospitalisationFormValidator)


class TestChildHospitalizationForm(TestModelMixin, TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(ChildPreviousHospitalisationFormValidator, *args, **kwargs)

    def setUp(self):
        appointment = Appointment.objects.create(
            subject_identifier='2334432-1',
            appt_datetime=get_utcnow(),
            visit_code='2001',
            visit_instance='0',
           )
        
        child_visit = ChildVisit.objects.create(
            appointment=appointment, )

        RegisteredSubject.objects.create(
            subject_identifier=appointment.subject_identifier,
            relative_identifier='2334432', )

        self.cleaned_data = {'child_visit': child_visit}

    def test_hospital_count_invalid(self):
        """
        Raise an error if the hospital name other is not captured.
        """
        self.cleaned_data.update({
            'hos_last_visit': YES,
            'hospitalized_count': None
            })

        form_validator = ChildPreviousHospitalisationFormValidator(
            cleaned_data=self.cleaned_data)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('hospitalized_count', form_validator._errors)


@tag('hozinline')
class TestChildHospitalizationFormInline(TestCase):

    def test_hospital_name_required_invalid(self):
        """
        Raise an error if the hospital name other is not captured.
        """
        ListModel.objects.create(name='chosp_other', short_name='chosp_other')
        cleaned_data = {
            'name_hospital': OTHER,
            'name_hospital_other': None,
            'reason_hospitalized': ListModel.objects.all(),
            'reason_hospitalized_other': 'testing'
            }

        form_validator = ChildPreHospitalisationInlineFormValidator(
            cleaned_data=cleaned_data)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('name_hospital_other', form_validator._errors)

    def test_surgical_reason_valid(self):
        ListModel.objects.create(name='chosp_other', short_name='chosp_other')

        cleaned_data = {
            'reason_hospitalized': ListModel.objects.all(),
            'reason_hospitalized_other': 'surgical',
            'surgical_reason': None
            }

        form_validator = ChildPreHospitalisationInlineFormValidator(
            cleaned_data=cleaned_data)
        try:
            form_validator.validate()
        except ValidationError as e:
            self.fail(f'ValidationError unexpectedly raised. Got{e}')
