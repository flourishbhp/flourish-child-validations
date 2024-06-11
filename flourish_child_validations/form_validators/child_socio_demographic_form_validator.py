from django.apps import apps as django_apps
from django.core.exceptions import ValidationError
from edc_base.utils import age, get_utcnow
from edc_constants.choices import NO, YES
from edc_form_validators import FormValidator

from .form_validator_mixin import ChildFormValidatorMixin
from ..utils import caregiver_subject_identifier


class ChildSocioDemographicFormValidator(ChildFormValidatorMixin, FormValidator):
    child_assent_model = 'flourish_child.childassent'
    caregiver_child_consent_model = 'flourish_caregiver.caregiverchildconsent'
    maternal_delivery_model = 'flourish_caregiver.maternaldelivery'
    caregiver_socio_demographic_model = 'flourish_caregiver.sociodemographicdata'

    def onschedule_model(self, instance=None):
        schedule = getattr(instance, 'schedule', None)
        return getattr(schedule, 'onschedule_model', None)

    def onschedule_model_cls(self, onschedule_model):
        return django_apps.get_model(onschedule_model)

    @property
    def caregiver_socio_demographic_cls(self):
        return django_apps.get_model(self.caregiver_socio_demographic_model)

    def clean(self):
        super().clean()
        self.subject_identifier = self.cleaned_data.get(
            'child_visit').appointment.subject_identifier

        self.validate_other_specify(
            field='primary_caretaker'
        )

        self.validate_other_specify(
            field='secondary_caretaker'
        )

        self.required_if(
            YES,
            field='house_painted',
            field_required='paint_peeling'
        )

        self.validate_consent_version_obj(self.subject_identifier)

        report_datetime = self.cleaned_data.get('report_datetime')

        self.validate_against_visit_datetime(report_datetime)
        self.validate_other_specify(field='ethnicity')
        self.validate_child_stay_with_caregiver(cleaned_data=self.cleaned_data)
        self.validate_other_specify(field='toilet_facility')

        self.validate_number_of_people_living_in_the_household(
            cleaned_data=self.cleaned_data)

        self.validate_child_not_schooling()

        self.validate_other_specify(field='education_level')

    def validate_child_stay_with_caregiver(self, cleaned_data=None):
        maternal_identifier = caregiver_subject_identifier(
            subject_identifier=self.subject_identifier,
            registered_subject_cls=self.registered_subject_cls)
        child_visit_code_sequence = self.cleaned_data.get(
            'child_visit').visit_code_sequence
        child_visit = self.cleaned_data.get(
            'child_visit').appointment.visit_code
        maternal_visit_code = str(child_visit) + 'M'
        caregiver_model_objs = self.caregiver_socio_demographic_cls.objects.filter(
            maternal_visit__visit_code=maternal_visit_code,
            maternal_visit__visit_code_sequence=child_visit_code_sequence,
            maternal_visit__subject_identifier=maternal_identifier, )

        for caregiver_model_obj in caregiver_model_objs:
            corresponding_visit = caregiver_model_obj.maternal_visit
            corresponding_onschedule_model = self.onschedule_model(
                instance=corresponding_visit)
            corresponding_onschedule_cls = self.onschedule_model_cls(
                corresponding_onschedule_model)

            try:
                corresponding_onschedule_cls.objects.get(
                    subject_identifier=maternal_identifier,
                    child_subject_identifier=self.subject_identifier,
                    schedule_name=corresponding_visit.schedule_name, )
            except corresponding_onschedule_cls.DoesNotExist:
                pass
            else:
                if (caregiver_model_obj.stay_with_child and
                        caregiver_model_obj.stay_with_child != cleaned_data.get(
                            'stay_with_caregiver')):
                    msg = {'stay_with_caregiver':
                               'Response should match the response provided '
                               'on the caregiver socio demographic data form'}
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

        if (attend_school == YES and
                self.cleaned_data.get('education_level') == 'no_schooling'):
            msg = {'education_level':
                       'This child is said to be attending school, Please specify '
                       'education level.'}
            self._errors.update(msg)
            raise ValidationError(msg)

        if (attend_school == NO and
                self.cleaned_data.get('education_level') != 'no_schooling'):
            msg = {'education_level':
                       'This child is not attending school, Please specify '
                       'education level as `No schooling` to indicate this.'}
            self._errors.update(msg)
            raise ValidationError(msg)

        self.applicable_if(
            YES,
            field='attend_school',
            field_applicable='school_type')

        boarding_responses = [
            'public_boarding_school',
            'private_boarding_school']

        self.required_if(
            *boarding_responses,
            field='school_type',
            field_required='months_in_boarding')

        self.applicable_if_true(
            self.child_age > 16 and attend_school == NO,
            field='attend_school',
            field_applicable='working')

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

        child_caregiver_consen_objs = child_caregiver_consent_model_cls.objects.filter(
            subject_identifier=self.subject_identifier)

        if child_caregiver_consen_objs:
            return child_caregiver_consen_objs.latest('consent_datetime')

    @property
    def maternal_delivery_obj(self):
        maternal_delivery_model_cls = django_apps.get_model(
            self.maternal_delivery_model)
        maternal_identifier = caregiver_subject_identifier(
            subject_identifier=self.subject_identifier,
            registered_subject_cls=self.registered_subject_cls, )
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
