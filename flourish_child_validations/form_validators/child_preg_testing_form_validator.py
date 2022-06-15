from attr import field
from django.core.exceptions import ValidationError
from edc_constants.constants import NO
from edc_form_validators import FormValidator
from django.apps import apps as django_apps
from edc_base.utils import get_utcnow
from dateutil.relativedelta import relativedelta
from .form_validator_mixin import ChildFormValidatorMixin
from edc_constants.constants import YES


class ChildPregTestingFormValidator(ChildFormValidatorMixin, FormValidator):
    
    child_caregiver_consent_model = 'flourish_caregiver.caregiverchildconsent'

    def clean(self):
        
        self.subject_identifier = self.cleaned_data.get(
            'child_visit').appointment.subject_identifier
        super().clean()
        
        self.visit_code = self.cleaned_data.get(
            'child_visit').appointment.visit_code
                
        all_fields = [ 'last_menstrual_period', 'is_lmp_date_estimated',]
        
        for field in all_fields:
            self.required_if(YES, field='menarche', field_required=field)
            
        self.required_if_true(self.visit_code == '2000', field_required='test_done') 
        test_done = self.cleaned_data.get('test_done')
        self.required_if_true(test_done==YES, field_required='test_date')  
        self.required_if_true(test_done==YES, field_required='preg_test_result')   
        self.validate_consent_version_obj(self.subject_identifier)
        self.validate_preg_test_result_required()
        self.validate_lmp()
        
    @property
    def child_caregiver_consent_model_cls(self):
        return django_apps.get_model(self.child_caregiver_consent_model)

    @property
    def caregiver_child_obj(self):

        caregiver_chld_consents = self.child_caregiver_consent_model_cls.objects.filter(
                subject_identifier=self.subject_identifier)

        if caregiver_chld_consents:
            return caregiver_chld_consents.latest('consent_datetime')   
        
         
    def validate_preg_test_result_required(self):
    
        self.required_if(YES,
                        field='test_done',
                        field_required='preg_test_result')     

    def validate_lmp(self):
        """A function to validate the participants menarche if it valid then 
        the lmp is validated to check if its above the 2months threshold
        and if it is then the pregnancy test is required
        """
        threshold_date = (get_utcnow() - relativedelta(months=2)).date()
        lmp = self.cleaned_data.get('last_menstrual_period')
        consent = self.caregiver_child_obj
        today_dt = get_utcnow().date()
        childvisit = self.cleaned_data.get('child_visit')

        if consent:
            if any(item in childvisit.schedule_name for item in ['qt','quart']):
                menarche = self.cleaned_data.get('menarche')
                if menarche == YES:
                    if lmp and lmp == today_dt:
                        message = {'last_menstrual_period': (
                            'Last Menstrual Period date cannot be today.')}
                        self._errors.update(message)
                        raise ValidationError(message)
                    elif lmp and lmp >= threshold_date:
                        self.required_if_true(lmp >= threshold_date,
                                                field_required='test_done')
                         
                    # elif lmp and lmp <= threshold_date:
                    #     self.not_required_if(lmp <= threshold_date,
                    #                             field_required='test_done')    


                    elif lmp is None:
                        message = {'last_menstrual_period': (
                            'Last Menstrual Period date cannot be left blank.')}
                        self._errors.update(message)
                        raise ValidationError(message)
                

            

            

                 
             
             
             
             
             
            
             
        
    