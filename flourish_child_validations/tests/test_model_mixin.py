class TestModeMixin:

    def __init__(self, validator_class, *args, **kwargs):
        super().__init__(*args, **kwargs)

        validator_class = validator_class

        validator_class.caregiver_consent_model = \
            'flourish_form_validations.subjectconsent'

        validator_class.subject_consent_model = \
            'flourish_form_validations.subjectconsent'

        validator_class.maternal_dataset_model = \
            'flourish_form_validations.maternaldataset'

        validator_class.child_dataset_model = \
            'flourish_form_validations.childdataset'

        validator_class.antenatal_enrollment_model = \
            'flourish_form_validations.antenatalenrollment'

        validator_class.subject_screening_model = \
            'flourish_form_validations.subjectscreening'

        validator_class.prior_screening_model = \
            'flourish_form_validations.subjectscreening'

        validator_class.arvs_pre_preg_model = \
            'flourish_form_validations.arvsprepregnancy'

        validator_class.preg_women_screening_model = \
            'flourish_form_validations.subjectscreening'

        validator_class.caregiver_locator_model = \
            'flourish_form_validations.caregiverlocator'

        validator_class.delivery_model = \
            'flourish_form_validations.maternaldelivery'

        validator_class.maternal_visit_model = \
            'flourish_form_validations.maternalvisit'

        validator_class.maternal_arv_model = \
            'flourish_form_validations.maternalarv'

        validator_class.arvs_pre_pregnancy = \
            'flourish_form_validations.maternalarvduringpreg'

        validator_class.ultrasound_model = \
            'flourish_form_validations.ultrasound'

        validator_class.screening_preg_women = \
            'flourish_form_validations.screeningpregwomen'

        validator_class.caregiver_offstudy_model = \
            'flourish_form_validations.offstudy'

        validator_class.caregiver_contact_model = \
            'flourish_form_validations.caregivercontact'

        validator_class.consent_version_model = \
            'flourish_form_validations.flourishconsentversion'

        validator_class.caregiver_locator_model = \
            'flourish_form_validations.caregiverlocator'

    class Meta:
        abstract = True