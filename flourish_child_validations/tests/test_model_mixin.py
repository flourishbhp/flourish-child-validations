class TestModeMixin:

    def __init__(self, validator_class, *args, **kwargs):
        super().__init__(*args, **kwargs)

        validator_class = validator_class

        validator_class.caregiver_consent_model = \
            'flourish_child_validations.subjectconsent'

        validator_class.subject_consent_model = \
            'flourish_child_validations.subjectconsent'
            
        validator_class.consent_version_model = \
            'flourish_child_validations.flourishconsentversion'

    class Meta:
        abstract = True