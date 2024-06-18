from django import forms
from django.apps import apps as django_apps
from django.core.exceptions import ValidationError
from edc_action_item.site_action_items import site_action_items
from edc_base.utils import age, get_utcnow
from edc_constants.constants import NEW

from ..utils import caregiver_subject_identifier


class ChildFormValidatorMixin:

    infant_birth_model = 'flourish_child.childbirth'
    subject_consent_model = 'flourish_caregiver.subjectconsent'
    child_offstudy_model = 'flourish_prn.childoffstudy'
    consent_version_model = 'flourish_caregiver.flourishconsentversion'
    registered_subject_model = 'edc_registration.registeredsubject'
    child_consent_model = 'flourish_caregiver.caregiverchildconsent'
    cohort_model = 'flourish_caregiver.cohort'

    @property
    def infant_birth_cls(self):
        return django_apps.get_model(self.infant_birth_model)

    @property
    def subject_consent_cls(self):
        return django_apps.get_model(self.subject_consent_model)

    @property
    def consent_version_cls(self):
        return django_apps.get_model(self.consent_version_model)

    @property
    def child_offstudy_cls(self):
        return django_apps.get_model(self.child_offstudy_model)

    @property
    def registered_subject_cls(self):
        return django_apps.get_model(self.registered_subject_model)

    @property
    def caregiver_child_consent_cls(self):
        return django_apps.get_model(self.child_consent_model)

    @property
    def cohort_model_cls(self):
        return django_apps.get_model(self.cohort_model)

    @property
    def child_consent_model_obj(self):
        try:
            return self.caregiver_child_consent_cls.objects.filter(
                subject_identifier=self.subject_identifier).latest(
                    'consent_datetime')
        except self.caregiver_child_consent_cls.DoesNotExist:
            return None

    @property
    def action_item_model_cls(self):
        action_cls = site_action_items.get(
            self.child_offstudy_cls.action_name)
        return action_cls.action_item_model_cls()

    def clean(self):
        if self.cleaned_data.get('child_visit'):
            self.subject_identifier = self.cleaned_data.get(
                'child_visit').subject_identifier
            self.validate_against_visit_datetime(
                self.cleaned_data.get('report_datetime'))
        else:
            self.subject_identifier = getattr(self, 'subject_identifier',
                                              None) or self.cleaned_data.get(
                'subject_identifier', None)

        self.validate_offstudy_model()
        super().clean()

    def validate_against_birth_date(self, infant_identifier=None,
                                    report_datetime=None, date_attr=None,
                                    message=None):

        try:
            infant_birth = self.infant_birth_cls.objects.get(
                subject_identifier=infant_identifier)
        except self.infant_birth_cls.DoesNotExist:
            raise ValidationError(
                'Please complete Infant Birth form '
                f'before proceeding.')
        else:
            if (report_datetime and
                    report_datetime < getattr(infant_birth, f'{date_attr}')):
                message = message or ('Report datetime cannot be before enrollment '
                                      'datetime.')
                raise forms.ValidationError(message)
            else:
                return infant_birth

    def validate_against_visit_datetime(self, report_datetime):
        if report_datetime and report_datetime < \
                self.cleaned_data.get('child_visit').report_datetime:
            raise forms.ValidationError(
                "Report datetime cannot be before visit datetime.")

    def validate_against_visit_date(self, offstudy_date):
        if offstudy_date and offstudy_date < \
                self.cleaned_data.get('child_visit').report_datetime.date():
            raise forms.ValidationError({
                'offstudy_date':
                    'offstudy date cannot be before visit date.'
            })

    def validate_offstudy_model(self):

        try:
            self.action_item_model_cls.objects.get(
                subject_identifier=self.subject_identifier,
                action_type__name='submit-childoff-study',
                status=NEW)
        except self.action_item_model_cls.DoesNotExist:
            try:
                self.child_offstudy_cls.objects.get(
                    subject_identifier=self.subject_identifier)
            except self.child_offstudy_cls.DoesNotExist:
                pass
            else:
                raise forms.ValidationError(
                    'Participant has been taken offstudy. Cannot capture any '
                    'new data.')
        else:
            raise forms.ValidationError(
                'Participant is scheduled to be taken offstudy without '
                'any new data collection. Cannot capture any new data.')

    def validate_consent_version_obj(self, subject_identifier):

        latest_consent_obj = self.latest_consent_obj(subject_identifier)

        if latest_consent_obj:
            try:
                self.consent_version_cls.objects.get(
                    screening_identifier=latest_consent_obj.screening_identifier)
            except self.consent_version_cls.DoesNotExist:
                raise forms.ValidationError(
                    'Consent version form has not been completed, kindly complete it '
                    'before'
                    ' continuing.')

    def latest_consent_obj(self, subject_identifier):
        maternal_identifier = caregiver_subject_identifier(
            subject_identifier=subject_identifier,
            registered_subject_cls=self.registered_subject_cls)
        subject_consents = self.subject_consent_cls.objects.filter(
            subject_identifier=maternal_identifier)

        if subject_consents:
            return subject_consents.latest('consent_datetime')

    def cohort_model_obj(self):
        try:
            return self.cohort_model_cls.objects.filter(
                subject_identifier=self.subject_identifier).latest('assign_datetime')
        except self.cohort_model_cls.DoesNotExist:
            raise ValidationError(
                {'__all__':
                 'Child does not have a cohort instance. Please contact '
                 'administrator for assistance'})

    @property
    def child_assent_obj(self):
        child_assent_model_cls = django_apps.get_model(self.child_assent_model)
        child_assent_objs = child_assent_model_cls.objects.filter(
            subject_identifier=self.subject_identifier)

        if child_assent_objs:
            return child_assent_objs.latest('consent_datetime')

    @property
    def child_caregiver_consent_obj(self):
        child_caregiver_consent_model_cls = django_apps.get_model(
            self.caregiver_child_consent_model)
        try:
            model_obj = child_caregiver_consent_model_cls.objects.filter(
                subject_identifier=self.subject_identifier).latest('consent_datetime')
        except child_caregiver_consent_model_cls.DoesNotExist:
            return None
        else:
            return model_obj

    @property
    def maternal_delivery_obj(self):
        maternal_delivery_model_cls = django_apps.get_model(
            self.maternal_delivery_model)
        maternal_identifier = caregiver_subject_identifier(
            subject_identifier=self.subject_identifier,
            registered_subject_cls=self.registered_subject_cls)
        try:
            model_obj = maternal_delivery_model_cls.objects.get(
                subject_identifier=maternal_identifier)
        except maternal_delivery_model_cls.DoesNotExist:
            return None
        else:
            return model_obj

    @property
    def child_age(self):
        if self.child_assent_obj:
            birth_date = self.child_assent_obj.dob
            years = age(birth_date, get_utcnow()).years + age(
                birth_date, get_utcnow()).months / 12
            return years
        elif self.child_caregiver_consent_obj:
            birth_date = self.child_caregiver_consent_obj.child_dob
            years = age(birth_date, get_utcnow()).years + age(
                birth_date, get_utcnow()).months / 12
            return years
        elif self.maternal_delivery_obj:
            birth_date = self.maternal_delivery_obj.delivery_datetime.date()
            years = age(birth_date, get_utcnow()).months / 12
            return years
        return 0
