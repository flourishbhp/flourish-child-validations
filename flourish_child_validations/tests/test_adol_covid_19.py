from django.test import TestCase, tag
from django.utils import timezone
from django.core.exceptions import ValidationError
from ..form_validators import Covid19AdolFormValidator
from .models import ChildVisit, Appointment
from .test_model_mixin import TestModeMixin


@tag('covid')
class TestCovid19FormValidator(TestModeMixin, TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(Covid19AdolFormValidator, *args, **kwargs)

    def setUp(self):
        appointment = Appointment.objects.create(
            subject_identifier='2334432',
            appt_datetime=timezone.now(),
            visit_code='2000',
            visit_instance='0')

        child_visit = ChildVisit.objects.create(
            subject_identifier='12345323',
            appointment=appointment)
        
        self.data = {
            'child_visit': child_visit,
            'test_for_covid': '',
            'receive_test_result': '',
            'result_of_test': ''
        }
        
        
    def test_receive_test_result_required(self):
        pass
    
    def test_result_of_test_required(self):
        pass
        