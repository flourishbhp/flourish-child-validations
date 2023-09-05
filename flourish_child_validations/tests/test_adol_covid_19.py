from django.test import TestCase, tag
from edc_base.utils import get_utcnow

from ..form_validators import Covid19AdolFormValidator
from .models import ChildVisit, Appointment, RegisteredSubject
from .test_model_mixin import TestModelMixin


@tag('covid')
class TestCovid19FormValidator(TestModelMixin, TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(Covid19AdolFormValidator, *args, **kwargs)

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
        