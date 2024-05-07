from django import forms
from django.apps import apps as django_apps
from django.core.exceptions import ValidationError
from edc_action_item.site_action_items import site_action_items
from edc_constants.constants import ON_STUDY, NEW, OFF_STUDY, YES, OTHER, NO
from edc_constants.constants import PARTICIPANT, ALIVE, DEAD
from edc_form_validators import FormValidator
from edc_visit_tracking.constants import COMPLETED_PROTOCOL_VISIT
from edc_visit_tracking.constants import LOST_VISIT, MISSED_VISIT, UNSCHEDULED
from edc_visit_tracking.form_validators import VisitFormValidator
from flourish_child.visit_sequence import VisitSequence
from flourish_prn.action_items import CHILDOFF_STUDY_ACTION

from .crf_offstudy_form_validator import CrfOffStudyFormValidator
from .form_validator_mixin import ChildFormValidatorMixin


class ChildVisitFormValidator(VisitFormValidator, CrfOffStudyFormValidator,
                              ChildFormValidatorMixin, FormValidator):

    caregiver_child_consent_model = 'flourish_caregiver.caregiverchildconsent'
    continued_consent_model = 'flourish_child.childcontinuedconsent'
    visit_sequence_cls = VisitSequence

    @property
    def caregiver_child_consent_cls(self):
        return django_apps.get_model(self.caregiver_child_consent_model)

    @property
    def continued_consent_cls(self):
        return django_apps.get_model(self.continued_consent_model)

    @property
    def continued_consent_exists(self):
        return self.continued_consent_cls.objects.filter(
            subject_identifier=self.subject_identifier).exists()

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

        self.validate_consent_version_obj(
            self.cleaned_data.get('appointment').subject_identifier)

        self.validate_is_present()

        self.validate_last_alive_date()

    def validate_is_present(self):

        reason = self.cleaned_data.get('reason')
        is_present = self.cleaned_data.get('is_present')
        info_source = self.cleaned_data.get('info_source')
        study_status = self.cleaned_data.get('study_status')

        if (reason == LOST_VISIT and study_status != OFF_STUDY):
            msg = {'study_status': 'Participant has been lost to follow up, '
                   'study status should be off study.'}
            self._errors.update(msg)
            raise ValidationError(msg)
        if (reason == COMPLETED_PROTOCOL_VISIT and study_status != OFF_STUDY):
            msg = {'study_status': 'Participant is completing protocol, '
                   'study status should be off study.'}
            self._errors.update(msg)
            raise ValidationError(msg)

        information_provider = self.cleaned_data.get('information_provider')

        if information_provider == 'self':

            if not self.continued_consent_exists:
                raise ValidationError(
                    {'information_provider':
                     'Continued consent not filled, hence the child cannot provide information without a guardian'})

            if info_source not in ['other_contact', PARTICIPANT]:
                raise ValidationError(
                    {'info_source':
                     'Participant is to provide the information'})

        if info_source != PARTICIPANT and is_present == YES:
            raise ValidationError(
                 {'is_present':
                  'Source of information must be from participant if participant is present.'})

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

        child_consents = self.caregiver_child_consent_cls.objects.filter(
            subject_identifier=self.cleaned_data.get('appointment').subject_identifier)

        if child_consents:
            latest_consent = child_consents.latest('consent_datetime')
            last_alive_date = self.cleaned_data.get('last_alive_date')
            if last_alive_date and latest_consent.child_dob:
                if last_alive_date < latest_consent.child_dob:
                    msg = {'last_alive_date': 'Date cannot be before birth date'}
                    self._errors.update(msg)
                    raise ValidationError(msg)
        else:
            raise forms.ValidationError('Missing Consent on Behalf of Child form for this'
                                        ' participant')

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
