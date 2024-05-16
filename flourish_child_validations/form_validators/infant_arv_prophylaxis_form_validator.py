from django.forms import ValidationError
from edc_constants.constants import YES, NO, OTHER
from edc_form_validators import FormValidator

from .crf_offstudy_form_validator import CrfOffStudyFormValidator
from .form_validator_mixin import ChildFormValidatorMixin


class InfantArvProphylaxisFormValidator(ChildFormValidatorMixin,
                                        CrfOffStudyFormValidator,
                                        FormValidator):

    infant_birth_model = 'flourish_child.childbirth'

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

        date_arvs_modified = self.cleaned_data.get('date_arvs_modified', None)
        self.validate_against_birth_date(
            infant_identifier=self.subject_identifier,
            report_datetime=date_arvs_modified,
            date_attr='dob',
            message={'date_arvs_modified':
                     'Date ARVs were modified can not be before child DOB.'})

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


class ChildArvProphDatesFormValidator(ChildFormValidatorMixin,
                                      CrfOffStudyFormValidator,
                                      FormValidator):

    infant_birth_model = 'flourish_child.childbirth'

    def clean(self):
        self.subject_identifier = self.cleaned_data.get(
             'infant_arv_proph').child_visit.subject_identifier
        super().clean()

        stop_date = self.cleaned_data.get('arv_stop_date', None)
        infant_arv_proph = self.cleaned_data.get('infant_arv_proph', None)
        art_status = getattr(infant_arv_proph, 'art_status', None)
        if art_status == 'in_progress' and stop_date:
            message = {'arv_stop_date':
                       'ARV status is still in progress, do not provide stop date.'}
            raise ValidationError(message)
        elif art_status != 'in_progress' and not stop_date:
            message = {'arv_stop_date':
                       f'ARV status is `{art_status}`, please provide stop date.'}
            raise ValidationError(message)

        start_date = self.cleaned_data.get('arv_start_date', None)
        stop_date = self.cleaned_data.get('arv_stop_date', None)
        self.validate_against_birth_date(
            infant_identifier=self.subject_identifier,
            report_datetime=start_date,
            date_attr='dob',
            message={'arv_start_date':
                     'ARV start date can not be before child DOB.'})

        if stop_date and stop_date < start_date:
            message = {'arv_stop_date':
                       'ARV stop date can not before start date.'}
            raise ValidationError(message)
