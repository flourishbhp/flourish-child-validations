from django.test import TestCase, tag
from django.utils import timezone
from django.core.exceptions import ValidationError
from edc_constants.constants import NO, YES, OTHER
from ..form_validators import TbPresenceHouseholdMembersAdolFormValidator
from .models import ChildVisit, Appointment, RegisteredSubject
from .test_model_mixin import TestModelMixin


@tag('adol_presence')
class TestTbPresenceHouseholdMembersAdolFormValidator(TestModelMixin, TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(TbPresenceHouseholdMembersAdolFormValidator, *args, **kwargs)

    def setUp(self):
        appointment = Appointment.objects.create(
            subject_identifier='2334432-1',
            appt_datetime=timezone.now(),
            visit_code='2000',
            visit_instance='0')

        child_visit = ChildVisit.objects.create(
            subject_identifier='2334432-1',
            appointment=appointment)

        RegisteredSubject.objects.create(
            subject_identifier=appointment.subject_identifier,
            relative_identifier='2334432')
        
        self.data = {
            'child_visit': child_visit,
            'tb_diagnosed': YES,
            'tb_ind_rel': 'partner',
            'tb_ind_other': None,
            'tb_referral': NO,
            'tb_in_house': YES,
            'cough_ind_rel': 'partner',
            'cough_ind_other': None,
            'fever_signs': YES,
            'fever_ind_rel': 'child',
            'fever_ind_other': None,
            'night_sweats': 'unknown',
            'sweat_ind_rel': None,
            'sweat_ind_other': None,
            'weight_loss': YES,
            'weight_ind_rel': 'partner',
            'weight_ind_other': None}
        
        
    def test_cough_ind_other_required(self):
        self.data['cough_ind_rel'] = OTHER
        
        
        form_validator = TbPresenceHouseholdMembersAdolFormValidator(cleaned_data=self.data)
        
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('cough_ind_other', form_validator._errors)
        
        
    def test_fever_ind_other_required(self):
        self.data['fever_ind_rel'] = OTHER
        
        
        form_validator = TbPresenceHouseholdMembersAdolFormValidator(cleaned_data=self.data)
        
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('fever_ind_other', form_validator._errors)