from django.test import TestCase, tag
from django.core.exceptions import ValidationError
from edc_base.utils import get_utcnow
from edc_constants.constants import YES, OTHER

from ..form_validators import HivKnowledgeFormValidator
from .models import (ChildVisit, Appointment, ActionItem, ActionType,
                     RegisteredSubject)
from .test_model_mixin import TestModelMixin


@tag('adol_hiv')
class TestHivKnowledgeFormValidator(TestModelMixin, TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(HivKnowledgeFormValidator, *args, **kwargs)

    def setUp(self):
        appointment = Appointment.objects.create(
            subject_identifier='2334432-1',
            appt_datetime=get_utcnow(),
            visit_code='2000',
            visit_instance='0')

        child_visit = ChildVisit.objects.create(
            appointment=appointment)

        RegisteredSubject.objects.create(
            subject_identifier=appointment.subject_identifier,
            relative_identifier='2334432')

        action_type = ActionType.objects.create(
            name='submit-childoff-study')

        ActionItem.objects.create(
            subject_identifier=appointment.subject_identifier,
            action_type=action_type)
        
        self.data = {
            'child_visit': child_visit,
            'hiv_informed': YES,
            'hiv_knowledge_medium_other': '',
            'fever_knowledge': YES,
            'cough_knowledge': YES,
            'night_sweats_knowledge': YES,
            'weight_loss_knowledge': YES,
            'rash_knowledge': YES,
            'headache_knowledge': YES,
            'vomiting_knowledge': YES,
            'body_ache_knowledge': YES,
            'other_knowledge': '',
            'hiv_utensils_transmit': YES,
            'hiv_air_transmit': YES,
            'hiv_sexual_transmit': YES,
            'hiv_sexual_transmit_other': '',
            'hiv_treatable': YES,
            'hiv_curable': YES,
            'hiv_community': '4',
            'hiv_community_treatment': OTHER,
            'hiv_community_treatment_other': 'jjj'}
        
    def test_hiv_community_treatment_other_required(self):
        
        self.data['hiv_community_treatment_other'] = None
        
        form_validator = HivKnowledgeFormValidator(cleaned_data=self.data)
        
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('hiv_community_treatment_other', form_validator._errors)
        
