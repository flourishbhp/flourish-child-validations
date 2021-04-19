from django import forms
from django.apps import apps as django_apps
from django.core.exceptions import ValidationError
from edc_action_item.site_action_items import site_action_items
from edc_constants.constants import ON_STUDY, NEW, OFF_STUDY, YES, OTHER
from edc_constants.constants import PARTICIPANT, ALIVE, DEAD
from edc_form_validators import FormValidator
from edc_visit_tracking.constants import COMPLETED_PROTOCOL_VISIT
from edc_visit_tracking.constants import SCHEDULED, LOST_VISIT, MISSED_VISIT, UNSCHEDULED
from edc_visit_tracking.form_validators import VisitFormValidator
from flourish_prn.action_items import CHILDOFF_STUDY_ACTION

from .crf_offstudy_form_validator import CrfOffStudyFormValidator


class ChildVisitFormValidator(VisitFormValidator, CrfOffStudyFormValidator,
                              FormValidator):

    def clean(self):
        cleaned_data = self.cleaned_data
        self.report_datetime = cleaned_data.get('report_datetime')

        self.subject_identifier = self.cleaned_data.get(
            'appointment').subject_identifier
        super().clean()

        self.validate_other_specify('information_provider')

        if self.instance:
            if not self.instance.id:
                self.validate_study_status()

        self.validate_death()

        self.validate_is_present()

        self.validate_last_alive_date()

    def validate_is_present(self):

        reason = self.cleaned_data.get('reason')

        if (reason == LOST_VISIT and
                self.cleaned_data.get('study_status') != OFF_STUDY):
            msg = {'study_status': 'Participant has been lost to follow up, '
                   'study status should be off study.'}
            self._errors.update(msg)
            raise ValidationError(msg)
        if (reason == COMPLETED_PROTOCOL_VISIT and
                self.cleaned_data.get('study_status') != OFF_STUDY):
            msg = {'study_status': 'Participant is completing protocol, '
                   'study status should be off study.'}
            self._errors.update(msg)
            raise ValidationError(msg)

        if self.cleaned_data.get('is_present') == YES:
            if self.cleaned_data.get('info_source') != PARTICIPANT:
                raise forms.ValidationError(
                    {'info_source': 'Source of information must be from '
                     'participant if participant is present.'})

    def validate_death(self):
        if (self.cleaned_data.get('survival_status') == DEAD
                and self.cleaned_data.get('study_status') != OFF_STUDY):
            msg = {'study_status': 'Participant is deceased, study status '
                   'should be off study.'}
            self._errors.update(msg)
            raise ValidationError(msg)
        if self.cleaned_data.get('survival_status') != ALIVE:
            if (self.cleaned_data.get('is_present') == YES
                    or self.cleaned_data.get('info_source') == PARTICIPANT):
                msg = {'survival_status': 'Participant cannot be present or '
                       'source of information if their survival status is not'
                       'alive.'}
                self._errors.update(msg)
                raise ValidationError(msg)

    def validate_last_alive_date(self):
        """Returns an instance of the current maternal consent or
        raises an exception if not found."""

        child_consent_cls = django_apps.get_model('flourish_caregiver.caregiverchildconsent')

        try:
            child_consent_obj = child_consent_cls.objects.get(
                subject_identifier=self.cleaned_data.get('appointment').subject_identifier)
        except child_consent_cls.DoesNotExist:
            raise forms.ValidationError('Missing Consent on Behalf of Child form for this'
                                        ' participant')
        else:
            last_alive_date = self.cleaned_data.get('last_alive_date')
            if last_alive_date and last_alive_date < child_consent_obj.child_dob:
                msg = {'last_alive_date': 'Date cannot be before birth date'}
                self._errors.update(msg)
                raise ValidationError(msg)

    def validate_reason_and_info_source(self):
        pass

    def validate_study_status(self):
        infant_offstudy_cls = django_apps.get_model(
            'flourish_prn.childoffstudy')
        action_cls = site_action_items.get(
            infant_offstudy_cls.action_name)
        action_item_model_cls = action_cls.action_item_model_cls()

        try:
            action_item = action_item_model_cls.objects.get(
                subject_identifier=self.cleaned_data.get(
                    'appointment').subject_identifier,
                action_type__name=CHILDOFF_STUDY_ACTION,
                status=NEW)
        except action_item_model_cls.DoesNotExist:
            try:
                infant_offstudy_cls.objects.get(
                    subject_identifier=self.cleaned_data.get('appointment').subject_identifier)
            except infant_offstudy_cls.DoesNotExist:
                pass
            else:
                if self.cleaned_data.get('study_status') == ON_STUDY:
                    raise forms.ValidationError(
                        {'study_status': 'Participant has been taken offstudy.'
                         ' Cannot be indicated as on study.'})
        else:
            if (action_item.parent_reference_model_obj
                and self.cleaned_data.get(
                    'report_datetime') >= action_item.parent_reference_model_obj.report_datetime):
                raise forms.ValidationError(
                    'Participant is scheduled to go offstudy.'
                    ' Cannot edit visit until offstudy form is completed.')

    def validate_required_fields(self):

        self.required_if(
            MISSED_VISIT,
            field='reason',
            field_required='reason_missed')

        self.required_if(
            UNSCHEDULED,
            field='reason',
            field_required='reason_unscheduled')

        self.required_if(
            OTHER,
            field='info_source',
            field_required='info_source_other')
