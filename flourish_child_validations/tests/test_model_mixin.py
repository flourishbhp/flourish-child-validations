from .models import ActionItem

class TestModelMixin:

    def __init__(self, validator_class, *args, **kwargs):
        super().__init__(*args, **kwargs)

        validator_class = validator_class

        validator_class.registered_subject_model = \
            'flourish_child_validations.registeredsubject'
    
        validator_class.caregiver_consent_model = \
            'flourish_child_validations.subjectconsent'

        validator_class.subject_consent_model = \
            'flourish_child_validations.subjectconsent'
            
        validator_class.consent_version_model = \
            'flourish_child_validations.flourishconsentversion'

        validator_class.prior_screening_model = \
            'flourish_child_validations.screeningpriorbhpparticipants'

        validator_class.child_dataset_model = \
            'flourish_child_validations.childdataset'
            
        validator_class.child_assent_model = \
            'flourish_child_validations.childassent'
  
        validator_class.caregiver_child_consent_model = \
            'flourish_child_validations.caregiverchildconsent'

        validator_class.child_offstudy_model = \
            'flourish_child_validations.childoffstudy'
            
        validator_class.action_item_model = \
            'flourish_child_validations.actionitem'

        validator_class.infant_feeding_model = \
            'flourish_child_validations.infantfeeding'

        validator_class.caregiver_socio_demographic_model = \
            'flourish_child_validations.caregiversociodemographicdata'

        validator_class.maternal_delivery_model = \
            'flourish_child_validations.maternaldelivery'

        validator_class.action_item_model_cls = ActionItem

    class Meta:
        abstract = True