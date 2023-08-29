from django.test import TestCase, tag
from edc_base.utils import get_utcnow
from edc_constants.constants import OTHER
from django.core.exceptions import ValidationError

from ..form_validators import TbReferralAdolFormValidator
from .models import ChildVisit, Appointment, RegisteredSubject
from .test_model_mixin import TestModelMixin


@tag('tb_ref')
class TestTbReferralFormValidator(TestModelMixin, TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(TbReferralAdolFormValidator, *args, **kwargs)

    def setUp(self):
        appointment = Appointment.objects.create(
            subject_identifier='2334432-1',
            appt_datetime=get_utcnow(),
            visit_code='2100A',
            visit_instance='0')

        child_visit = ChildVisit.objects.create(
            subject_identifier='2334432-1',
            appointment=appointment)

        RegisteredSubject.objects.create(
            subject_identifier=appointment.subject_identifier,
            relative_identifier='2334432')
        
        self.data = {
            'child_visit': child_visit,
            'report_datetime': get_utcnow(),
            'referral_date': get_utcnow().date(),  
            'location': 'g_west',
            'location_other': None
        }
        
        
    def test_location_other_required(self):
        self.data['location'] = OTHER
        
        form_validator = TbReferralAdolFormValidator(cleaned_data=self.data)
        
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('location_other', form_validator._errors)
    
        