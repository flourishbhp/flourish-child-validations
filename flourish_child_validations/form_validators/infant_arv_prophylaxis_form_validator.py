from edc_constants.constants import YES, NO, OTHER
from edc_form_validators import FormValidator

from .crf_offstudy_form_validator import CrfOffStudyFormValidator
from .form_validator_mixin import ChildFormValidatorMixin


class InfantArvProphylaxisFormValidator(ChildFormValidatorMixin,
                                        CrfOffStudyFormValidator,
                                        FormValidator):

    def clean(self):
        self.subject_identifier = self.cleaned_data.get(
            'child_visit').appointment.subject_identifier
        super().clean()

        self.validate_consent_version_obj(self.subject_identifier)

        self.validate_against_visit_datetime(
            self.cleaned_data.get('report_datetime'))

        self.required_if(NO,
                         field='took_art_proph',
                         field_required='reason_no_art')

        self.required_if(OTHER,
                         field='reason_no_art',
                         field_required='reason_no_art_other')

        self.required_if(YES,
                         field='took_art_proph',
                         field_required='art_status')

        self.required_if('completed_gt_28days',
                         field='art_status',
                         field_required='days_art_received')

        self.required_if('incomplete',
                         field='art_status',
                         field_required='reason_incomplete')

        self.required_if(YES,
                         field='took_art_proph',
                         field_required='arvs_modified')

        fields_required = ['date_arvs_modified', 'reason_modified']
        for field_required in fields_required:
            self.required_if(YES,
                             field='arvs_modified',
                             field_required=field_required)

        self.required_if('side_effects',
                         field='reason_modified',
                         field_required='specify_effects')

        self.required_if(OTHER,
                         field='reason_modified',
                         field_required='reason_modified_othr')

        self.required_if(YES,
                         field='took_art_proph',
                         field_required='missed_dose')

        fields_required = ['missed_dose_count', 'reason_missed']
        for field_required in fields_required:
            self.required_if(YES,
                             field='missed_dose',
                             field_required=field_required)
