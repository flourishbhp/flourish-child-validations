from django.apps import apps as django_apps
from django.core.exceptions import ValidationError
from edc_base.utils import age, get_utcnow
from edc_form_validators import FormValidator


class VaccinesReceivedFormValidator(FormValidator):

    caregiver_child_consent = 'flourish_caregiver.caregiverchildconsent'

    @property
    def caregiver_child_consent_cls(self):
        return django_apps.get_model(self.caregiver_child_consent)

    def clean(self):
        self.subject_identifier = self.cleaned_data.get(
            'child_immunization_history').subject_identifier
        received_vaccine_name = self.cleaned_data.get('received_vaccine_name')
        if self.caregiver_child_consent_model:
            child_dob = self.caregiver_child_consent_model.child_dob
            child_age = age(child_dob, get_utcnow().date()).years
            if child_age <= 12 and received_vaccine_name == 'hpv_vaccine':
                message = {'received_vaccine_name':
                           'Child age is less than 12, cannot select HPV vaccine'}
                self._errors.update(message)
                raise ValidationError(message)

    @property
    def caregiver_child_consent_model(self):
        try:
            caregiver_child = self.caregiver_child_consent_cls.objects.get(
                subject_identifier=self.subject_identifier)
        except self.caregiver_child_consent_cls.DoesNotExist:
            return None
        else:
            return caregiver_child
