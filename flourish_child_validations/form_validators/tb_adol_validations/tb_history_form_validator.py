from django.apps import apps as django_apps
from edc_form_validators import FormValidator
from edc_constants.constants import OTHER, YES, UNKNOWN
from ..form_validator_mixin import ChildFormValidatorMixin

class TbHistoryFormValidator(ChildFormValidatorMixin, FormValidator):
      
      
    def clean(self):
        super().clean()
        
        self.validate_tb_preventative_therapy()
        
        
        self.required_if(YES, 
                         field='prior_tb_history', 
                         field_required='tb_diagnosis_type')
        
        self.required_if('outside_the_lungs', 'both', 
                         field='tb_diagnosis_type', 
                         field_required='extra_pulmonary_loc')
        
        self.required_if('outside_the_lungs', 'both', 
                         field='tb_diagnosis_type', 
                         field_required='extra_pulmonary_loc')
        
        self.not_required_if('outside_the_lungs', 'both', 
                         field='tb_diagnosis_type', 
                         field_required='prior_treatmnt_history')
        
        self.validate_prior_treatment_history()
          
    def validate_tb_preventative_therapy(self):
        
        required_fields = [
            'reason_for_therapy',
            'therapy_prescribed_age',
            'tbt_completed',
        ]
        
        for field in required_fields:
            self.required_if(YES,
                             field='history_of_tbt', 
                             field_required=field)
            
    def validate_prior_treatment_history(self):
        

        
        required_fields = [
            'tb_drugs_freq',
            'iv_meds_used',
            'tb_treatmnt_completed'
        ]
        
        for field in required_fields:
            self.required_if(YES, 
                             field='prior_treatmnt_history',
                             field_required=field)