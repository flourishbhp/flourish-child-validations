from django.apps import apps as django_apps
from django.core.exceptions import ValidationError

from edc_base.utils import age, get_utcnow
from edc_constants.choices import NO, YES
from edc_form_validators import FormValidator

from .form_validator_mixin import ChildFormValidatorMixin


class ChildSocioDemographicFormValidator(ChildFormValidatorMixin, FormValidator):

    child_assent_model = 'flourish_child.childassent'

    child_caregiver_consent_model = 'flourish_caregiver.caregiverchildconsent'

    maternal_delivery_model = 'flourish_caregiver.maternaldelivery'

    caregiver_socio_demographic_model = 'flourish_caregiver.sociodemographicdata'

    @property
    def caregiver_socio_demographic_cls(self):
        return django_apps.get_model(self.caregiver_socio_demographic_model)

    def clean(self):
        self.subject_identifier = self.cleaned_data.get(
            'child_visit').appointment.subject_identifier
        super().clean()

        report_datetime = self.cleaned_data.get('report_datetime')

        self.validate_against_visit_datetime(report_datetime)
        self.validate_other_specify(field='ethnicity')
        self.validate_child_stay_with_caregiver(cleaned_data=self.cleaned_data)
        self.validate_other_specify(field='toilet_facility')

        self.validate_number_of_people_living_in_the_household(
            cleaned_data=self.cleaned_data)

        self.required_if(YES, field='attend_school',
                         field_required='education_level')
        self.validate_child_not_schooling()

        self.validate_other_specify(field='education_level')

    @property
    def caregiver_subject_identifier(self):
        subject_identifier = self.subject_identifier.split('-')
        subject_identifier.pop()
        caregiver_subject_identifier = '-'.join(subject_identifier)
        return caregiver_subject_identifier

    def validate_child_stay_with_caregiver(self, cleaned_data=None):

        caregiver_subject_identifier = self.caregiver_subject_identifier
        try:
            caregiver_model_obj = \
                self.caregiver_socio_demographic_cls.objects.get(
                    maternal_visit__appointment__subject_identifier=caregiver_subject_identifier)
        except self.caregiver_socio_demographic_cls.DoesNotExist:
            raise ValidationError('Please complete the caregiver socio '
                                  'demographic data form')
        else:
            if caregiver_model_obj.stay_with_child != cleaned_data.get(
                    'stay_with_caregiver'):
                msg = {'stay_with_caregiver':
                       'Response should match the response provided on the '
                       'caregiver socio demographic data form'}
                self._errors.update(msg)
                raise ValidationError(msg)

    def validate_number_of_people_living_in_the_household(self,
                                                          cleaned_data=None):
        older_than18 = cleaned_data.get('older_than18')
        house_people_number = cleaned_data.get('house_people_number')
        if older_than18 and (older_than18 >
                             house_people_number):
            msg = {'older_than18':
                   f'Number of people ({older_than18}) who are older than 18 '
                   f'and live in the household cannot be more than the total '
                   f'number ({house_people_number}) of people living in the '
                   f'household'}
            self._errors.update(msg)
            raise ValidationError(msg)

    def validate_child_not_schooling(self):
        attend_school = self.cleaned_data.get('attend_school')
        working = self.cleaned_data.get('working')

        if self.child_age > 16:
            self.applicable_if(NO, field='attend_school',
                               field_applicable='working')

        if attend_school == NO:
            if self.child_age > 16 and working is None:
                msg = {'working':
                       'Adolescent is more than 16 years, This field is '
                       'applicable'}
                self._errors.update(msg)
                raise ValidationError(msg)

            elif self.child_age < 16 and working is not None:
                msg = {'working':
                       'Child is less than 16, This field is not applicable'}
                self._errors.update(msg)
                raise ValidationError(msg)
        else:
            self.not_required_if(YES, field='attend_school',
                                 field_required='working')

    @property
    def child_assent_obj(self):
        child_assent_model_cls = django_apps.get_model(self.child_assent_model)
        try:
            model_obj = child_assent_model_cls.objects.get(
                subject_identifier=self.subject_identifier)
        except child_assent_model_cls.DoesNotExist:
            return None
        else:
            return model_obj

    @property
    def child_caregiver_consent_obj(self):
        child_caregiver_consent_model_cls = django_apps.get_model(
            self.child_caregiver_consent_model)
        try:
            model_obj = child_caregiver_consent_model_cls.objects.get(
                subject_identifier=self.subject_identifier)
        except child_caregiver_consent_model_cls.DoesNotExist:
            return None
        else:
            return model_obj

    @property
    def maternal_delivery_obj(self):
        maternal_delivery_model_cls = django_apps.get_model(
            self.maternal_delivery_model)
        try:
            model_obj = maternal_delivery_model_cls.objects.get(
                subject_identifier__istartswith=self.subject_identifier)
        except maternal_delivery_model_cls.DoesNotExist:
            return None
        else:
            return model_obj

    @property
    def child_age(self):
        if self.child_assent_obj:
            birth_date = self.child_assent_obj.dob
            years = age(birth_date, get_utcnow()).years
            return years
        elif self.child_caregiver_consent_obj:
            birth_date = self.child_caregiver_consent_obj.child_dob
            years = age(birth_date, get_utcnow()).years
            return years
        elif self.maternal_delivery_obj:
            birth_date = self.maternal_delivery_obj.delivery_datetime.date()
            years = age(birth_date, get_utcnow()).months
            return years
        return 0
